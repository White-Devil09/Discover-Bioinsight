from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["SECRET_KEY"] = "e3741824f313dc9b23da24ebd4cfe5af31c578a6"
app.config["MONGO_URI"] = "mongodb+srv://bhanu:bhanu123@cluster1.gpwosqi.mongodb.net/Patient_database?retryWrites=true&w=majority"
app.config['STATIC_FOLDER'] = 'static'

mongo = PyMongo(app)
db = mongo.db 

from application import routes