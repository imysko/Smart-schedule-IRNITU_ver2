from flask import Flask
from app import views

app = Flask(__name__)

app.add_url_rule('/', view_func=views.IndexView.as_view('index'))