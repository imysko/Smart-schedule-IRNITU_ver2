from flask import Flask
from app import views

app = Flask(__name__)

app.add_url_rule('/api/find_week/', view_func=views.FindWeekView.as_view('find_week'))