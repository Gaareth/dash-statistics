# Partly edited code by HealYouDown
"""
MIT License

Copyright (c) 2020 HealYouDown

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
from collections import defaultdict
from typing import List, Tuple

from flask_sqlalchemy import BaseQuery, Model, SQLAlchemy
from sqlalchemy import desc, func, and_


class StatisticsQueries:
    def __init__(self, db: SQLAlchemy, model: Model):
        self.db = db
        self.model = model

    def _add_date_filter_to_query(
            self,
            query: BaseQuery,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ) -> BaseQuery:
        # unsure if this works
        return query.filter(and_(func.date(self.model.date) >= start_date),
                            func.date(self.model.date) <= end_date)

    def get_number_of_unique_visitors(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ) -> int:
        query = (self.db.session.query(self.model)
                 .group_by(self.model.remote_address))

        query = self._add_date_filter_to_query(query,
                                               start_date,
                                               end_date)

        return query.count()

    def get_statistic_data(self, column_name):
        """ Returns the available labels of a db column with the according frequency """
        query = self.db.session.query(getattr(self.model, column_name), func.count(getattr(self.model, column_name))).\
            group_by(getattr(self.model, column_name)).order_by(desc(column_name))
        data_labels, data_values = map(list, zip(*query.all()))
        return data_labels, data_values

    def get_routes_data(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ) -> List:
        query = (self.db.session.query(self.model.path,
                                       func.count(self.model.path).label("hits"),
                                       func.count(self.model.remote_address.distinct()).label("unique_hits"),
                                       func.max(self.model.date).label("last_requested"),
                                       func.avg(self.model.response_time).label("average_response_time"))
                 .group_by(self.model.path)
                 .order_by(desc("hits")))

        query = self._add_date_filter_to_query(query,
                                               start_date,
                                               end_date)

        return query.all()

    def get_requests_for_path(
            self,
            path: str,
            start_date: datetime.datetime,
            end_date: datetime.datetime
    ) -> List:
        query = (self.db.session.query(self.model)
                 .filter(self.model.path == path)
                 .order_by(self.model.date.desc()))

        query = self._add_date_filter_to_query(query,
                                               start_date,
                                               end_date)

        return query.all()

    def get_user_chart_data(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            path: str = None,
    ) -> Tuple[List[dict], List[dict]]:
        query = (self.db.session.query(self.model.date,
                                       self.model.remote_address))

        query = self._add_date_filter_to_query(query,
                                               start_date,
                                               end_date)

        if path is not None:
            query = query.filter(self.model.path == path)

        requests = query.all()

        hits_dict = defaultdict(int)
        unique_hits_dict = defaultdict(set)

        for req in requests:
            hits_dict[str(req.date.date())] += 1
            unique_hits_dict[str(req.date.date())].add(req.remote_address)

        hits = [{"x": date, "y": count} for date, count in hits_dict.items()]
        unique_hits = [{"x": date, "y": len(ip_set)} for date, ip_set in unique_hits_dict.items()]

        return hits, unique_hits
