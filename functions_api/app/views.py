import json

from flask.views import View

from app.functions import find_week


class BaseView(View):

    def functions_data(self):
        raise NotImplementedError

    def dispatch_request(self):
        data = self.functions_data()
        return json.dumps(data)


class FindWeekView(BaseView):
    """Определеие четности недели"""

    def functions_data(self):
        return find_week.find_week()
