import datetime

import dash_html_components as html
# from .statistics import colors

from .utils import header, search_section, hits_chart, stats_table, initial_date

from dash.dependencies import Output, Input, State


def callbacks(app, api, dash_prefix):
    """ Updates route view with new datetime data """
    @app.callback(
        Output('route_view', 'children'),
        [Input('update-button', 'n_clicks'),
         State('startdate-input', 'value'),
         State('enddate-input', 'value'),
         State("url", "search")]
    )
    def update(n_clicks, start_date, end_date, search):
        return view(api, datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                    datetime.datetime.strptime(end_date, "%Y-%m-%d"), search.split("?path=")[1], dash_prefix)


def table_data(api, start_date: datetime.datetime, end_date: datetime.datetime, path: str, column_names: dict = None):
    """  Format information of a single route/path/url for the Dash Datatable

    :param api: reference to StatisticQueries
    :param start_date: date range start
    :param end_date: date range end
    :param path: route for which the data should be shown
    :param column_names: Dictionary specifying which database columns and the according text/title should be displayed
                         in the html table. Structure: {"column_name": "displayed title"}
                         Default: {
                                "path": "URL",
                                "method": "Method",
                                "status_code": "Status",
                                "response_time": "Duration",
                                "date": "Date",
                                "remote_address": "IP Address",
                                "user_country_name": "Location",
                                "platform": "Operating System",
                                "browser": "Browser"
                                }
    :return:    List with lists containing column values:
                e.g: [
                        ["path url"],
                        ["method"],
                        ["the status code"]
                ] and the corresponding titles which should be displayed
    """
    if column_names is None:
        column_names = {
            "path": "URL",
            "method": "Method",
            "status_code": "Status",
            "response_time": "Duration in [s]",
            "date": "Date [UTC]",
            "remote_address": "IP Address",
            "user_country_name": "Location",
            "platform": "Operating System",
            "browser": "Browser"
        }

    requests = api.get_requests_for_path(path, start_date, end_date)

    # performance issues?
    # Purpose: Only use specified column_names
    return [
               [vars(request).get(column_name) for column_name in column_names]
               for request in requests
           ], column_names.values()


def view(api, start_date, end_date, path, dash_prefix):
    if start_date is None:
        start_date = initial_date(api)

    start_date = start_date.date()
    end_date = end_date.date()

    data_values, data_labels = table_data(api, start_date, end_date, path)

    return html.Div(id="route_view", children=[
        header(path, dash_prefix),
        html.Div(className="container-fluid px-1", style={}, children=[
            search_section(api, start_date, end_date),
            hits_chart(api, start_date, end_date, path, plot_title=f"Total Hits for {path}"),
            stats_table(data=data_values, data_labels=data_labels),
        ])
    ])
