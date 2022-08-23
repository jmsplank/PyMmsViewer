from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path
from typing import Any

import requests

from . import logger
from .consts import DRATE, INSTRUMENT


def url_create(
    base_type: str,
    start_date: str,
    end_date: str,
    prb: int,
    instrument: INSTRUMENT,
    drate: DRATE,
    lvl: str,
) -> str:
    """create a url using lasp api

    Args:
        base_type (str): base url to lasp server e.g. https://lasp.colorado.edu/mms/sdc/public/files/api/v1/file_info/
        start_date (str): formatted yyyy-mm-dd(-hh-mm-ss)
        end_date (str): formatted yyyy-mm-dd(-hh-mm-ss
        prb (int): probe, mms 1-4
        instrument (INSTRUMENT): e.g. FGM, FPI
        drate (DRATE): data rate, fast or survey
        lvl (str): product level, usually 'l2

    Returns:
        str: a url
    """
    url = (
        base_type
        + "science?start_date="
        + start_date
        + "&end_date="
        + end_date
        + "&sc_id=mms"
        + str(prb)
        + "&instrument_id="
        + instrument
        + "&data_rate_mode="
        + drate
        + "&data_level="
        + lvl
    )
    return url


def url_file_search(
    start_date: str,
    end_date: str,
    prb: int,
    instrument: INSTRUMENT,
    drate: DRATE,
    lvl: str,
) -> str:
    """Implementation of url_create that uses the file_info url

    Args:
        start_date (str): formatted yyyy-mm-dd(-hh-mm-ss)
        end_date (str): formatted yyyy-mm-dd(-hh-mm-ss
        prb (int): probe, mms 1-4
        instrument (INSTRUMENT): e.g. FGM, FPI
        drate (DRATE): data rate, fast or survey
        lvl (str): product level, usually 'l2

    Returns:
        str: a url
    """
    return url_create(
        "https://lasp.colorado.edu/mms/sdc/public/files/api/v1/file_info/",
        start_date,
        end_date,
        prb,
        instrument,
        drate,
        lvl,
    )


def create_trange_from_dt(start: dt, end: dt, long: bool = False) -> tuple[str, str]:
    """converts two datetime objects into strings accepted by lasp server.

    Use long flag to choose between selecting an entire day or specific times (i.e. long format)
    if long:
        yyyy-mm-dd-hh-mm-ss
    else:
        yyyy-mm-dd

    Args:
        start (dt): start datetime
        end (dt): end datetime
        long (bool, optional): use exact hh-mm-ss times for trange instead of whole day. Defaults to False.

    Returns:
        tuple[str, str]: (yyyy-mm-dd, yyyy-mm-dd-hh-mm-ss) if not long
            (yyyy-mm-dd-hh-mm-ss, yyyy-mm-dd-hh-mm-ss) if long
    """
    fmt = "%Y-%m-%d"
    fmt_long = fmt + "-%H-%M-%S"
    if long:
        start_str = dt.strftime(start, fmt_long)
        end_str = dt.strftime(end, fmt_long)
    else:
        start_str = dt.strftime(start, fmt)
        # add one day minus one second to start of day
        end_day = dt.strptime(start_str, fmt) + timedelta(days=1, seconds=-1)
        end_str = dt.strftime(end_day, fmt_long)

    return start_str, end_str


def test_combinations(inst: INSTRUMENT, drate: DRATE) -> None:
    """Raise error if bad set of configurations used

    Args:
        inst (INSTRUMENT): instrument to test
        drate (DRATE): data rate to test

    Raises:
        ValueError: incompatible values
    """
    bad_combos = {INSTRUMENT.FGM: [DRATE.FAST], INSTRUMENT.FPI: [DRATE.SURVEY]}

    if drate in bad_combos[inst]:
        raise ValueError(f"instrument {inst} incompatible with data rate {drate}")


def files_in_trange(
    trange: tuple[str, str],
    instrument: INSTRUMENT,
    prb: int = 1,
    drate: DRATE = DRATE.FAST,
) -> list[dict[str, Any]]:
    """Query lasp & return files

    Args:
        trange (tuple[str, str]): (start_date, end_date) formatted either 'YYYY-MM-DD' or 'YYYY-MM-DD-HH-MM-SS
        instrument (INSTRUMENT): Instrument type
        prb (int, optional): Probe number 1-4. Defaults to 1.
        drate (DRATE, optional): Data rate, normally one of DRATE.FAST or DRATE.SURVEY. Defaults to DRATE.FAST.

    Returns:
        List of files with info.
            dict format
            {
                "file_name": "mms1_fgm_srvy_l2_20180313_v5.130.0.cdf",
                "file_size": 68616367,                                      <- bytes
                "timetag": "2018-03-13T00:00:00",
                "modified_date": "2018-04-15T11:22:53",
            }
    """

    test_combinations(instrument, drate)

    url = url_file_search(
        start_date=trange[0],
        end_date=trange[1],
        prb=prb,
        instrument=instrument,
        drate=drate,
        lvl="l2",
    )
    res = requests.get(url).json()
    logger.debug(res)
    return res["files"]


def get_output_name(base_path: str | Path, file_name: str | Path) -> Path:
    """Generate path to base_path, check & create folder structure

    Args:
        base_path (str | Path): Folder structure to create, can be relative to ececution dir
        file_name (str | Path): name to save file as

    Returns:
        Path: path to save, all subdirectories created
    """
    if not isinstance(base_path, Path):
        base_path = Path(base_path)
    out = base_path / file_name
    out.mkdir(parents=True, exist_ok=True)
    return out


def download_file(fname: str, save_dir: Path) -> None:
    """Download file with specific name from server

    Args:
        fname (str): name of file must match what is on server
        save_dir (Path): Output path including filename to write bytes to
    """
    url = (
        "https://lasp.colorado.edu/mms/sdc/public/files/api/v1/download/science?file="
        + fname
    )
    logger.info(f"Requesting file {fname} from server")
    res = requests.get(url)
    logger.info("Writing response to file")
    save_dir.write_bytes(res.content)
