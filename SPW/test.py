import flask
from form import LoginForm
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://root:root@localhost:1433/users_db?driver=ODBC Driver 17 for SQL Server"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"
login_manager.login_message = "Please login to continue"
login_manager.login_message_category = "info"

# @login_manager.unauthorized_handler
# def unauthorized():
#     # do stuff
#     return a_response

class Users(UserMixin, db.Model):
    def __init__(self, active=True):
        self.username = db.Column(db.String(250), unique=True, nullable=False)
        self.password = db.Column(db.String(250), nullable=False)
        self.id = db.Column(db.Integer, primary_key=True)
        self.active = active

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


db.init_app(app)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(id):
    u = Users.session.get(id)
    return Users(u.username,u.id,u.active)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(Users.session.get(id))

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


# @app.route('/register', methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         user = Users(username=request.form.get("username"),password=request.form.get("password"))
#         db.session.add(user)
#         db.session.commit()
#         return redirect(url_for("login"))
#     return render_template("sign_up.html")
#
#
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         user = Users.query.filter_by(username=request.form.get("username")).first()
#         if user.password == request.form.get("password"):
#             login_user(user)
#             return redirect(url_for("home"))
#     return render_template("login.html")
#
#
# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for("home"))
#
#
# @app.route("/")
# def home():
#     return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
