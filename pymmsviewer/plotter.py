import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from . import logger


def make_fgm_figure(data: pd.DataFrame, approx_num_points: int = 1000) -> Figure:
    """create and return a line plot of mms fgm data. can be brst or srvy

    Args:
        data (pd.DataFrame): dataframe containing bx,by,bz,bt
        approx_num_points (int, optional): Number of points to plot for very large datasets. Defaults to 1000.

    Returns:
        Figure: the figure, fully formatted
    """
    if data.shape[0] > 3000:
        logger.debug(data.shape[0])

        step = int(data.shape[0] / approx_num_points)
        data = data.iloc[::step]
        data.index = pd.to_datetime(data.index, unit="s")

    fig = px.line(
        data, x=data.index, y=["bx", "by", "bz", "bt"], title="Magnetic Field"
    )
    return fig
