from flask.views import View


class IndexView(View):
    """отображение стартовой страницы"""

    def dispatch_request(self):
        return 'Ку!'
