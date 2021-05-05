import dash_html_components as html
from datetime import datetime, date, timedelta
# from .statistics import colors

import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "plotly_white"
from dash.dependencies import Output, Input, State

from .utils import header, search_section, basic_stats, hits_chart, stats_table, initial_date

from flask import url_for


def callbacks(app, api, dash_prefix):
    """ Updates index view with new datetime data """

    @app.callback(
        Output('index_view', 'children'),
        [Input('update-button', 'n_clicks'),
         State('startdate-input', 'value'),
         State('enddate-input', 'value')]
    )
    def update(n_clicks, start_date, end_date):
        return view(api, datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.strptime(end_date, "%Y-%m-%d"), dash_prefix)


# TODO: more flexible
def table_data(api, start_date, end_date, dash_prefix):
    """ Format information of the routes for the Dash Datatable

        :returns: List with lists containing column values:
                e.g: [
                        ["[URL](actual link for the url)"],
                        [hits],
                        [unique hits],
                        [last requested],
                        [average response duration]
                ] and the corresponding column names
    """
    column_names = ["URL", "Hits", "Unique Hits", "Last requested", "Avg. Duration in [s]"]
    routes = api.get_routes_data(start_date, end_date)

    return [
               [
                   f"[{entry}]({dash_prefix}?path={entry})" if i == 0 else entry
                   for i, entry in enumerate(list(route))
               ] for route in routes
           ], column_names


def view(api, start_date, end_date, dash_prefix):
    if start_date is None:
        start_date = initial_date(api)

    start_date = start_date.date()
    end_date = end_date.date()
    data_values, data_labels = table_data(api, start_date, end_date, dash_prefix)

    return html.Div(id="index_view", children=[
        header(None, dash_prefix),
        html.Div(className="px-1", style={}, children=[
                search_section(api, start_date, end_date),
                basic_stats(api, start_date, end_date),
                hits_chart(api, start_date, end_date),
                stats_table(data_values, data_labels),
            ]
        )
    ])
