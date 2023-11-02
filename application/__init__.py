from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "e3741824f313dc9b23da24ebd4cfe5af31c578a6"
app.config['STATIC_FOLDER'] = 'static'

from application import routes