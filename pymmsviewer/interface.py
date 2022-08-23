from typing import Any

from dash import Dash, dcc, html
from dash.dependencies import Component
from plotly.graph_objects import Figure


def simple_layout(a: Dash, kids: list[Component]) -> html.Div:
    """The main layout object, has a title and accepts additional components

    Args:
        a (Dash): the dash app
        kids (list[Component]): html components that make up the dashboard content

    Returns:
        html.Div: a div that can be assigned to app.layout
    """
    return html.Div(
        id="parent",  # type: ignore
        children=[
            html.H1(
                id="title",  # type: ignore
                children="Python MMS Viewer",
                style={"textAlign": "center", "marginTop": 40, "marginBottom": 40},  # type: ignore
            )
        ]
        + kids,
    )


def create_event(
    trange: tuple[str, str], files: list[dict[str, Any]], figure: Figure
) -> html.Div:
    """structure of event box shows a trange as well as files constructed from. Shows a figure too

    Args:
        trange (tuple[str, str]): the trange to show as event title
        files (list[dict[str, Any]]): the file names to list as data source
        figure (Figure): a figure object e.g. plot of FGM b components

    Returns:
        html.Div: a div that can be nested in app.layout somewhere
    """
    return html.Div(
        id="event-container",  # type: ignore
        children=[
            html.H3(children=f"{trange[0]} -> {trange[1]}"),
            html.P(children="\n".join([f["file_name"] for f in files])),
            dcc.Graph(figure=figure),  # type: ignore
        ],
    )
