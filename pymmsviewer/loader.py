import re
from pathlib import Path

import cdflib
import numpy as np
import pandas as pd

from . import logger


def match_list_to_regex(pattern: str, var_list: list[str]) -> str:
    """extract first match to regex pattern from list of zVariables

    Args:
        pattern (str): regex pattern
        var_list (list[str]): list of zVariables

    Raises:
        ValueError: If no match found in veriables

    Returns:
        str: the first match only
    """
    re_b = re.compile(pattern)
    b_matches = list(filter(re_b.match, var_list))
    if not b_matches:
        raise ValueError(
            "Could not find a variable within zVariables that matches fgm_b"
        )
    return b_matches[0]


def load_fgm_file(fpath: Path) -> pd.DataFrame:
    """use cdflib to load a fgm data file into a dataframe

    Args:
        fpath (Path): filepath for the data

    Returns:
        pd.DataFrame: the data with time as index and ['bx','by','bz','bt'] as columns
    """
    cdf: cdflib.cdfread.CDF = cdflib.CDF(fpath)
    info = cdf.cdf_info()
    zvars = info["zVariables"]
    logger.debug(f"{zvars=}")
    time = cdflib.cdfepoch.unixtime(cdf.varget("Epoch", to_np=True))
    b_pattern = "mms[0-9]_fgm_b_gse_(?:srvy|brst)_l2"
    bvar = match_list_to_regex(b_pattern, zvars)
    B: np.ndarray = cdf.varget(bvar)

    data = pd.DataFrame(B, index=time, columns=["bx", "by", "bz", "bt"])
    return data
