from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://root:root@localhost:1433/users_db?driver=ODBC Driver 17 for SQL Server"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()
db.init_app(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()
    uu = Users.query.filter_by(username='amiket').first()
    print(uu.password)