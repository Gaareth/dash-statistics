import time
import datetime
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
import requests
from dash.dependencies import Input, Output, State
from flask import Response, g, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlalchemy.sql import sqltypes

from . import index_view, route_view
from .StatisticsQueries import StatisticsQueries


class DashStatistics:

    def __init__(self, app: flask.app.Flask, prefix: str, db_colums: dict = None, app_name: str = "", **kwargs):
        self.BLACKLIST = ["_dash-component-suites", "_dash-dependencies", "_dash-layout", "_dash-update-component"]

        if db_colums is None:
            db_colums = {
                'response_time': sqltypes.Float,
                'date': sqltypes.DateTime,
                'method': sqltypes.String,
                'size': sqltypes.Integer,
                'status_code': sqltypes.Integer,
                'path': sqltypes.String,
                'user_agent': sqltypes.String,
                'remote_address': sqltypes.String,
                'exception': sqltypes.String,
                'referrer': sqltypes.String,
                'browser': sqltypes.String,
                'platform': sqltypes.String,
                'mimetype': sqltypes.String,

                'user_country_code': sqltypes.String,
                'user_country_name': sqltypes.String,
                'user_region_code': sqltypes.String,
                'user_region_name': sqltypes.String,
                'user_city': sqltypes.String,
                'user_zip_code': sqltypes.String,
                'user_time_zone': sqltypes.String,
                'user_latitude': sqltypes.Float,
                'user_longitude': sqltypes.Float,

            }

        self.app = app
        self.prefix = prefix
        self.app_name = app_name

        self.create_model(db_colums)
        self.api = StatisticsQueries(self.db, self.model)

        self.dash_app = self.init_dashboard()
        self.init_callbacks()

        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.teardown_request(self.teardown_request)

        if "disable_f" in kwargs:
            self.disable_f = kwargs["disable_f"]

    def create_model(self, db_columns):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///statistics.db'
        self.db = SQLAlchemy(self.app)

        class Request(self.db.Model):
            __tablename__ = "statistics"

            index = self.db.Column(self.db.Integer, primary_key=True, autoincrement=True)
            """
            for k, v in db_columns.items():
                print(f"{k}, {self.db.Column(v)}")
                setattr(self, k, self.db.Column(v))
            print(self.path)
            """
            response_time = self.db.Column(self.db.Float)
            date = self.db.Column(self.db.DateTime)
            method = self.db.Column(self.db.String)
            size = self.db.Column(self.db.Integer)
            status_code = self.db.Column(self.db.Integer)
            path = self.db.Column(self.db.String)
            user_agent = self.db.Column(self.db.String)
            remote_address = self.db.Column(self.db.String)
            exception = self.db.Column(self.db.String)
            referrer = self.db.Column(self.db.String)
            browser = self.db.Column(self.db.String)
            platform = self.db.Column(self.db.String)
            mimetype = self.db.Column(self.db.String)

            user_country_code = self.db.Column(self.db.String)
            user_country_name = self.db.Column(self.db.String)
            user_region_code = self.db.Column(self.db.String)
            user_region_name = self.db.Column(self.db.String)
            user_city = self.db.Column(self.db.String)
            user_zip_code = self.db.Column(self.db.String)
            user_time_zone = self.db.Column(self.db.String)
            user_latitude = self.db.Column(self.db.String)
            user_longitude = self.db.Column(self.db.String)

        try:
            self.db.create_all()
        except (exc.OperationalError, exc.ProgrammingError):
            print("Table already exists!")
        self.model = Request

    def init_dashboard(self) -> dash.Dash:
        """Create a Plotly Dash dashboard."""
        dash_app = dash.Dash(
            name=__name__,
            server=self.app,
            routes_pathname_prefix=self.prefix,
            external_stylesheets=[
                {
                    'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
                    'rel': 'stylesheet',
                    'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
                    'crossorigin': 'anonymous'
                }
            ],
            external_scripts=[
                {
                    'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js',
                    'integrity': 'sha384-JEW9xMcG8R+pH31jmWH6WWP0WintQrMb4s7ZOdauHnUtxwoG2vI5DkLtS3qm9Ekf',
                    'crossorigin': 'anonymous'
                }
            ],
            meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ],
        )
        dash_app.title = f"{self.app_name} - Statistics"
        dash_app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])

        return dash_app

    def init_callbacks(self):
        index_view.callbacks(self.dash_app, self.api, self.prefix)
        route_view.callbacks(self.dash_app, self.api, self.prefix)

        @self.dash_app.callback(Output('page-content', 'children'),
                                [Input('url', 'pathname'), State("url", "search")])
        def display_page(pathname, search):
            print(pathname)
            print(search)
            if self.prefix == pathname and "path" not in search:
                return index_view.view(self.api, None, datetime.datetime.now(), self.prefix)
            elif "?path=" in search:
                return route_view.view(self.api, None, datetime.datetime.now(), search.split("?path=")[1], self.prefix)
            else:
                return index_view.view(self.api, None, datetime.datetime.now(), self.prefix)

    def is_blacklisted(self):
        """ Determine if the requested path is an unwanted url, which should not be counted as a hit """
        for blacklisted in self.BLACKLIST:
            if blacklisted in request.path:
                return True
        return False

    def before_request(
            self
    ) -> None:
        """Function that is called before a request is processed.

        Args:
            self:
        """

        if self.disable_f():
            return None

        # Take time when request started
        g.start_time = time.time()
        g.request_date = datetime.datetime.utcnow()
        # after_request, which is used to get the status code,
        # is skipped if an error occures, so we set a default
        # error code that is used when this happens
        g.request_status_code = 500

    def after_request(
            self,
            response: Response
    ) -> Response:
        """Function that is called after a request was processed.

        Args:
            self:
            response (Response):
        """

        if self.disable_f():
            return response

        g.request_status_code = response.status_code
        g.request_content_size = response.content_length
        g.mimetype = response.mimetype

        return response

    def teardown_request(
            self,
            exception: Exception = None
    ) -> None:
        """Function that is called after a request, whether it was successful or
        not.

        Args:
            self:
            exception (Exception):
        """

        try:
            if self.disable_f() or self.is_blacklisted():
                return None

            # Take time when request ended
            end_time = time.time()
            # Create object that is later stored in database
            obj = {"response_time": end_time - g.start_time, "status_code": g.request_status_code,
                   "size": g.request_content_size, "method": request.method, "path": request.path,
                   "referrer": request.referrer, "browser": "{browser} {version}".format(
                    browser=request.user_agent.browser,
                    version=request.user_agent.version), "platform": request.user_agent.platform,
                   "user_agent": request.user_agent.string, "date": g.request_date, "mimetype": g.mimetype,
                   "exception": None if exception is None else repr(exception),
                   "remote_address": (request.environ['REMOTE_ADDR'])}

            # Gets geo data based of ip
            ip = request.remote_addr if request.remote_addr != "127.0.0.1" else ""
            # the api does not work with '127.0.0.1' but with "" for the localhost

            url = "https://freegeoip.app/json/{0}".format(ip)
            with requests.get(url) as req:
                if req.status_code != 403:  # 403 means rate limit was reached
                    resp = req.json()

                    none_if_empty = lambda s: None if resp.get(s) == "" else resp.get(s)  # noqa F731

                    obj["user_country_code"] = none_if_empty("country_code")
                    obj["user_country_name"] = none_if_empty("country_name")
                    obj["user_region_code"] = none_if_empty("region_code")
                    obj["user_region_name"] = none_if_empty("region_name")
                    obj["user_city"] = none_if_empty("city")
                    obj["user_zip_code"] = none_if_empty("zip_code")
                    obj["user_time_zone"] = none_if_empty("time_zone")
                    obj["user_latitude"] = none_if_empty("latitude")
                    obj["user_longitude"] = none_if_empty("longitude")

            # Adds object to db and saves
            self.db.session.add(
                self.model(**obj)
            )
            self.db.session.commit()
        except Exception as e:
            self.app.logger.warning("Error in dash-statistics teardown: " + str(e))

    def disable_f(self):
        """ Return False if this request should be recorded. Can be overridden by user. """
        return False
