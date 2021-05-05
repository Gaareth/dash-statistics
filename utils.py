import dash_table
import pandas as pd
from .StatisticsQueries import StatisticsQueries
import dash_core_components as dcc
from datetime import datetime, date, timedelta
import dash_html_components as html

import plotly.graph_objects as go


def breadcrumb_header(path, dash_prefix):
    if path is not None:
        return html.Nav(children=[
            html.Ol(className="breadcrumb mb-0", style={
                "padding": ".3rem",
            }, children=[
                html.Li(className="breadcrumb-item", children=[
                    html.A("Statistics", href=dash_prefix)
                ]),

                html.Li(f"{path}", className="breadcrumb-item active", **{'aria-current': "page"}),
            ])
        ])
    else:
        return html.Div()


def header(path: str, dash_prefix: str):
    return html.Nav(className="navbar navbar-expand-lg navbar-light bg-light", style={"padding-left": ".5rem"},
                    children=[
                        html.Div(className="container-fluid", children=[
                            html.A("Statistics", className="navbar-brand",
                                   style={"font-weight": "bold", "font-size": "1.5rem"}, href=dash_prefix),

                            html.Button(className="navbar-toggler", type="button", **{
                                'data-bs-toggle': "collapse",
                                'data-bs-target': "#header-dropdown",
                                'aria-controls': "header-dropdown",
                                'aria-expanded': "false",
                                'aria-label': "Toggle navigation",
                            }, children=[
                                html.Span(className="navbar-toggler-icon")
                            ]),
                            html.Div(id="header-dropdown", className="collapse navbar-collapse", children=[
                                html.Div(className="navbar-nav", children=[
                                    html.A("Back to Homepage", className="nav-link", href="/")
                                ]),
                                breadcrumb_header(path, dash_prefix)

                            ])
                        ]), html.Hr()
                    ])


def initial_date(api):
    query = (api.db.session.query(api.model.date).filter(api.model.index == 1))
    return query.all()[0][0]


def hits_chart(api, start_date: datetime, end_date: datetime, path: str = None, plot_title: str = "Total Hits"):
    user_chart_data = api.get_user_chart_data(start_date, end_date, path)
    hits_y = [kv["y"] for kv in user_chart_data[0]]
    hits_x = [kv["x"] for kv in user_chart_data[0]]

    unique_y = [kv["y"] for kv in user_chart_data[1]]
    unique_x = [kv["x"] for kv in user_chart_data[1]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hits_x, y=hits_y, name="Hits",
                             hovertemplate="%{x} || Hits: %{y}"))
    fig.add_trace(go.Scatter(x=unique_x, y=unique_y, name="Unique Hits",
                             hovertemplate="%{x} || Unique Hits: %{y}"))

    CONF = {
        "plot_bgcolor": "white",
        "paper_bgcolor": "white",
        "xaxis": {"color": "Gray", "fixedrange": True},
        "yaxis": {"color": "Gray", "visible": True, "fixedrange": True}
    }

    fig.update_layout(title=plot_title,
                      xaxis_title='Date',
                      yaxis_title='Number of Hits',
                      legend=dict(
                          orientation="h",
                          y=0,
                      ),
                      margin=dict(
                          l=0,
                          r=0,
                          b=0,
                          t=50,
                          pad=0
                      )
                      )
    fig.update_xaxes(tickformat="%b %e\n%Y", fixedrange=True)
    fig.update_yaxes(fixedrange=True)

    limited_interactions_config = {"scrollZoom": True, "dragMode": False,
                                   'modeBarButtonsToRemove': ["zoom2d", "zoomIn2d", "zoomOut2d"]}

    return html.Div(className="row justify-content-md-center", children=[
        html.Div(className="col-md-10", children=[
            html.Div(className="card", children=[
                html.Div(className="card-body px-1", children=[
                    dcc.Graph(figure=fig, config=limited_interactions_config)
                ])
            ])
        ])
    ])


def stats_table(data, data_labels):
    df = pd.DataFrame(data, columns=data_labels)

    # TODO: make global date_columns list
    for date_column in ["Date", "Last requested"]:
        if date_column in df.columns:
            df[date_column] = df[date_column].dt.strftime("%H:%M:%S %Y-%m-%d")

    return html.Div(className="row justify-content-md-center", children=[
        html.Div(className="col-md-10", style={"overflow-x": "auto"}, children=[
            dash_table.DataTable(
                id='stats-table',
                columns=[
                    {'name': column, "id": column, "type": 'text', "presentation": 'markdown'}
                    for i, column in enumerate(df.columns)],
                data=df.to_dict('records'),

                style_cell={
                    'textAlign': 'left',
                    'font-family': "arial",
                },
                style_header={
                    'fontWeight': 'bold'
                },
                style_data_conditional=[{
                    "if": {
                        'column_id': ["URL", "path"]
                    },
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 350,
                }],

                filter_action="native",
                sort_action="native",
                sort_mode="multi",

            )
        ])
    ])


def search_section(api, start_date: datetime, end_date: datetime):
    return html.Div(className="search_section", children=[
        html.Div(className="input-form-column", children=[
            html.Label("Start Date", id='startdate-input-label', htmlFor='startdate-input'),
            dcc.Input(
                id='startdate-input',
                className="input-form",
                type='Date',
                value=start_date
            )]
                 ),
        html.Div(className="input-form-column", children=[
            html.Label("End Date", id='enddate-input-label', htmlFor='enddate-input'),
            dcc.Input(
                id='enddate-input',
                className="input-form",
                type='Date',
                value=end_date
            )]
                 ),
        html.Div(className="input-form-submit", children=[
            html.Button("Update", id="update-button", className="btn btn-success")
        ]),
    ])


def card(title, *paragraphs):
    text = [html.P(x, className="card-text") for x in [*paragraphs]]

    return html.Div(className="card drop-shadow", children=[
        html.Div(className="card-body", children=[
            html.H4(title, className="card-title"), *text
        ])
    ])


def data_to_pie_chart(data):
    fig = go.Figure(go.Pie(labels=data[0], values=data[1]))
    fig.update_layout(margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ), legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    # fig.update_yaxes(automargin=True)
    return dcc.Graph(figure=fig, responsive=True)


def basic_stats(api: StatisticsQueries, start_date: datetime, end_date: datetime, data_columns: dict = None):
    """ Generate basic stats, including text and chart statistics


        @param api: reference to StatisticsQueries object
        @param data_columns: Dictionary specifying which database columns and what title should be displayed as a pie chart 
        {{column_name: chart_title}}. Example: {{'browser': "Browser"}}. Default: 
        {{"browser": "Browser", "user_country_name": "Country Name", "platform": "Platform"}}
    """

    if data_columns is None:
        data_columns = {"browser": "Browser", "user_country_name": "Country Name", "platform": "Platform"}
        # Default data columns

    routes = api.get_routes_data(start_date,
                                 end_date)
    hits = sum([route.hits for route in routes])
    unique_users = api.get_number_of_unique_visitors(start_date,
                                                     end_date)
    url_most_frequent = routes[0]

    return html.Div(id="statistics", style={"margin": "25px 0"}, children=[
        html.Div(id="basic_stats", style={"margin": "25px 5px"}, children=[
            html.Div(id="basic_stats_container", className="row", children=[
                html.Div(className="col-sm", children=[
                    card(f"{hits}", "Total Hits"),
                ]),
                html.Div(className="col-sm", children=[
                    card(f"{unique_users}", "Total Unique Hits", ),
                ]),
                html.Div(className="col-sm", children=[
                    card(f"{url_most_frequent[0]}", "Most clicked URL"),
                ]),
            ]),
        ]),

        html.Div(id="basic_stats_charts", className="row justify-content-md-center", children=
        [
            html.Div(className=f"py-1 col-md-{round(10 / len(data_columns))}",
                     style={"max-height": "500px", "min-height": "300px"}, children=[
                    html.Div(className="card h100", children=[
                        html.Div(className="card-body h100", children=[
                            html.H4(f"{data_columns[column_name]} Pie Chart", className="card-title"),
                            html.Div(className="pie-chart-wrapper h100 py-1", children=[
                                data_to_pie_chart(api.get_statistic_data(column_name))
                            ])
                        ])
                    ])
                ])
            for column_name in data_columns
        ])
    ])
