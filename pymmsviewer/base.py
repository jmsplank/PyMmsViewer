from datetime import datetime as dt
from pathlib import Path

from dash import Dash

from . import consts as cs
from . import logger
from .interface import create_event, simple_layout
from .lasp_api import create_trange_from_dt, download_file, files_in_trange
from .loader import load_fgm_file
from .plotter import make_fgm_figure

DEBUG_PATH = "/Users/jamesplank/Documents/PHD/PyMmsViewer/temp_data"

app = Dash()
app.title = "PyMmsViewer"

trange = create_trange_from_dt(*[dt.strptime("2018-03-13", "%Y-%m-%d")] * 2, long=False)
logger.debug(f"{trange=}")
files = files_in_trange(
    trange=trange, instrument=cs.INSTRUMENT.FGM, drate=cs.DRATE.SURVEY
)

outname: Path = Path(DEBUG_PATH) / files[0]["file_name"]
if not outname.exists():
    download_file(files[0]["file_name"], outname)

data = load_fgm_file(outname)
fig = make_fgm_figure(data, approx_num_points=10000)

app.layout = simple_layout(app, [create_event(trange, files, fig)])
