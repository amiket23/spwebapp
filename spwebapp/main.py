# Import required modules
import configparser
import re

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# Read config from ini file
config = configparser.ConfigParser()
config.read("./config.ini")
# Create the application
app = Flask(__name__)

# Define the configuration for your application
app.config["SQLALCHEMY_DATABASE_URI"] = config["sql"]["uri"]
app.config["SECRET_KEY"] = config["flask"]["session_secret"]
app.static_folder = "./static"
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)
# Initialize database and cryptography
db = SQLAlchemy()
bcrypt = Bcrypt(app)


# Define Security header
@app.after_request
def add_security_header(response):
    """
    Function to define security headers
    :param response:
    :return:
    """
    response.headers[
        "Content-Security-Policy-Report-Only"
    ] = "default-src 'none'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self'; frame-ancestors 'self'; form-action 'self';"
    response.headers["Server"] = "Not Gonna Tell Ya"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


# Define login manager/handler
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"
login_manager.login_message = "Please login to continue"
login_manager.login_message_category = "info"

# Initialize protection against cross site request forgery
csrf = CSRFProtect()
csrf.init_app(app)


# This function handles unauthorized login attempts
@login_manager.unauthorized_handler
def unauthorized():
    """
    :return: return to login page if user is unauthorized
    """
    return redirect("/login")


# This class defines the schema model for users table in the database
class Users(UserMixin, db.Model):
    """
    id - primary key
    username - unique identifier for login, not nullable.
    password - Secret key for each user, not nullable. Stored after hashing.
    email - unique for each user, not nullable.
    accesslevel - default value set to user.
    isactive - default value set to yes.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(13), unique=True, nullable=False)
    password = db.Column(db.String(12, 128), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    accesslevel = db.Column(db.String(13), default="user", nullable=False)
    isactive = db.Column(db.String(3), default="yes", nullable=False)


# This class defines the schema model for products table in the database
class Products(db.Model):
    """
    id - primary key
    name - product name, not nullable.
    brand - brand name for product, not nullable.
    code - unique identifier for each product, not nullable.
    price - price value for each product.
    image - name of the image file for the product stored in /static/images.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    brand = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(128), nullable=False)


# This class defines the schema model for orders table in the database
class Orders(db.Model):
    """
    order_id - primary key
    product - product code, unique identifier for product, not nullable.
    name - product name, not nullable.
    username - username of the logged in user.
    email - email of the logged in user.
    price - price value for the product.
    quantity - quantity ordered for the product.
    Address - Delivery address for the specific order.
    """

    order_id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    price = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.String(128), nullable=False)
    Address = db.Column(db.String(128), nullable=False)


# Add the initialized db to the application context
db.init_app(app)


# This function creates database values if they do not already exist.
with app.app_context():
    db.create_all()


# Function to load the user in login manager
@login_manager.user_loader
def user_loader(user_id):
    try:
        return Users.query.get(user_id)
    except Exception as e:
        return "Oops....Unexpected error. Contact Site Administrator if it persists."


# Define the endpoint for admin portal
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """
    Function to check user's access level for admin capabilities.
    :return: return to admin portal if user's access level is admin or redirect to index
    """
    try:
        user = Users.query.filter_by(id=session["_user_id"]).first()
    except Exception as e:
        return print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )
    if user.accesslevel:
        if user.accesslevel == "admin":
            try:
                product = Products.query.all()
                return render_template("admin.html", products=product)
            except Exception as e:
                print(
                    "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
                )
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


# Define the endpoint for registration portal
@app.route("/sign_up", methods=["GET", "POST"])
def register():
    """
    GET - renders registration page.
    POST - Function to register user in the database. It checks if username, password and email
    are not null and creates user in db.
    :return: returns to login page after user creation or to registration page if request is GET or
    returns to sign up page and displays error message in case of issues.
    """
    if request.method == "POST":
        if (
            request.form.get("username")
            or request.form.get("password")
            or request.form.get("email")
        ):
            if len(request.form.get("username")) > 13:
                flash("Username can be max 13 characters.")
                return redirect(url_for("register"))
            elif len(request.form.get("password")) > 128:
                flash("Password can be max 128 characters.")
                return redirect(url_for("register"))
            elif len(request.form.get("email")) > 30:
                flash("Email can be max 30 characters.")
                return redirect(url_for("register"))
            elif bool(
                re.match("^[a-zA-Z0-9]*$", request.form.get("username")) == False
            ):
                flash("Username cannot contain any special characters")
                return redirect(url_for("register"))
            elif len(request.form.get("password")) < 12:
                flash("Password should be minimum 12 characters")
                return redirect(url_for("register"))
            try:
                user = Users(
                    username=request.form.get("username"),
                    password=bcrypt.generate_password_hash(
                        request.form.get("password")
                    ).decode("utf-8"),
                    email=request.form.get("email"),
                )
                db.session.add(user)
                db.session.commit()
                flash("User Created. You can now log in")
                return redirect(url_for("login"))
            except Exception as e:
                flash(
                    "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
                )
                return redirect(url_for("register"))
        flash("one of the required fields is blank")
        return redirect(url_for("register"))
    if session['_user_id']:
        return redirect(url_for("index"))
    return render_template("sign_up.html")


# Define the endpoint for login portal
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET - renders login page.
    POST - Checks user's login credentials and logs them in if they match stored hash values from database.
    :return: returns user to home page with successful login message if creds match or
    returns user to login page with error message if creds do not match.
    """
    if request.method == "POST":
        if request.form.get("username") or request.form.get("password"):
            try:
                user = Users.query.filter_by(
                    username=request.form.get("username")
                ).first()
                if user is None:
                    flash("Incorrect Username")
                    return redirect(url_for("login"))
                if bcrypt.check_password_hash(
                    user.password, request.form.get("password")
                ):
                    if user.isactive == "yes":
                        login_user(user)
                        flash("You are now logged in")
                        if user.accesslevel == "admin":
                            return redirect(url_for("admin"))
                        if user.accesslevel == "fulfillment":
                            return redirect(url_for("orders"))
                        return redirect(url_for("home"))
                    flash("Your account is disabled. Contact administrator")
                    return redirect(url_for("login"))
                flash("Incorrect Password")
            except Exception as e:
                print(
                    "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
                )
            return redirect(url_for("login"))
        flash("one of the required fields is blank")
        return redirect(url_for("login"))
    return render_template("login.html")


# Define the endpoint for logout portal
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    function to logout currently logged in user.
    :return: returns to home page with user logged out message
    """
    try:
        logout_user()
        session.clear()
        flash("You have been logged out")
        return redirect(url_for("home"))
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define the endpoint for default path
@app.route("/")
def default_path():
    """
    :return: returns to home page
    """
    return render_template("index.html")


# Define the endpoint for the index page
@app.route("/index")
def index():
    """
    :return: returns to home page
    """
    return render_template("index.html")


# Define the endpoint for home page
@app.route("/home")
def home():
    """
    :return: returns to home page
    """
    return render_template("index.html")


# Define the endpoint for about page
@app.route("/about")
def about():
    """
    :return: returns to about page
    """
    return render_template("about.html")


# Define the endpoint for contact page
@app.route("/contact")
def contact():
    """
    :return: returns to contact page
    """
    return render_template("contact.html")


# Define the endpoint for frequently asked questions page
@app.route("/faq")
def faq():
    """
    :return: returns to page faq page
    """
    return render_template("faq.html")


# Define the endpoint for orders management portal
@app.route("/orders")
@login_required
def orders():
    """
    function checks if currently logged in user has the role 'fulfillment'
    and also loads the orders info into the page.
    :return: returns to order management page if user has the right role
    or redirects to index if user does not have fulfillment role.
    """
    try:
        user = Users.query.filter_by(id=session["_user_id"]).first()
        if user.accesslevel == "fulfillment":
            total_orders = Orders.query.all()
            return render_template("orders.html", orders=total_orders)
        else:
            return redirect(url_for("index"))
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define the endpoint for adding items to cart
@app.route("/add", methods=["POST"])
@login_required
def add_product_to_cart():
    """
    function builds a cart array from the chosen product and adds it to the user's cart
    :return: returns updated cart to the user
    """
    try:
        _quantity = int(request.form["quantity"])
        _code = request.form["code"]
        # validate the received values
        if _quantity and _code and request.method == "POST":
            product_value = ""
            product_list = Products.query.all()
            for product in product_list:
                if product.code == _code:
                    product_value = product
                    break
            product = product_value
            itemArray = {
                product.code: {
                    "name": product.name,
                    "code": product.code,
                    "quantity": _quantity,
                    "price": product.price,
                    "image": product.image,
                    "total_price": _quantity * product.price,
                }
            }

            all_total_price = 0
            all_total_quantity = 0
            session.modified = True
            if "cart_item" in session:
                if session["cart_item"] is not None:
                    if product.code in session["cart_item"]:
                        for key, value in session["cart_item"].items():
                            if product.code == key:
                                old_quantity = session["cart_item"][key]["quantity"]
                                total_quantity = old_quantity + _quantity
                                session["cart_item"][key]["quantity"] = total_quantity
                                session["cart_item"][key]["total_price"] = (
                                    total_quantity * product.price
                                )
                    else:
                        session["cart_item"] = array_merge(
                            session["cart_item"], itemArray
                        )

                    for key, value in session["cart_item"].items():
                        individual_quantity = int(session["cart_item"][key]["quantity"])
                        individual_price = float(
                            session["cart_item"][key]["total_price"]
                        )
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                else:
                    session["cart_item"] = itemArray
                    all_total_quantity = all_total_quantity + _quantity
                    all_total_price = all_total_price + _quantity * product.price
            else:
                session["cart_item"] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * product.price

            session["all_total_quantity"] = all_total_quantity
            session["all_total_price"] = all_total_price
            return redirect(url_for("shop"))
        else:
            return "Error while adding item to cart"
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define endpoint for shop page
@app.route("/shop", methods=["GET"])
@login_required
def shop():
    """
    function loads product values into the shop page. Login is required.
    :return: returns logged in user to the shop page
    """
    try:
        product = Products.query.all()
        return render_template("shop.html", products=product)
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define the endpoint for emptying cart
@app.route("/empty")
@login_required
def empty_cart():
    """
    function to empty the user's cart
    :return: returns user to the shop page after emptying the cart
    """
    try:
        session["cart_item"] = None
        return redirect(url_for("shop"))
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define the endpoint for checkout/cart page
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart_load():
    """
    function checks if user's access role is user or not
    GET - if access role is user then renders the checkout page
    POST - if access role is user then user can place orders
    :return: GET returns user to checkout page if accesslevel is user or
    returns user to index page if accesslevels is not user
    """
    try:
        user = Users.query.filter_by(id=session["_user_id"]).first()
        if user.accesslevel == "admin" or user.accesslevel == "fulfillment":
            return redirect(url_for("index"))
        if request.method == "POST":
            total_items = []
            if "cart_item" in session:
                if session["cart_item"] is not None:
                    for item in (session["cart_item"]).keys():
                        total_items.append(session["cart_item"][item])
            for item in total_items:
                user = Users.query.filter_by(id=session["_user_id"]).first()
                Address = (
                    request.form.get("fullname")
                    + ", "
                    + request.form.get("address")
                    + ", "
                    + request.form.get("city")
                    + ", "
                    + request.form.get("eir")
                )
                order = Orders(
                    product=item["code"],
                    name=item["name"],
                    username=user.username,
                    email=user.email,
                    price=item["price"],
                    quantity=item["quantity"],
                    Address=Address,
                )
                db.session.add(order)
                db.session.commit()
            return redirect(url_for("empty_cart"))
        total_items = []
        if "cart_item" in session:
            if session["cart_item"] is not None:
                for item in (session["cart_item"]).keys():
                    total_items.append(session["cart_item"][item])
                total_items_count = len(total_items)
                return render_template(
                    "checkout.html",
                    total_items=total_items,
                    total_items_count=total_items_count,
                )
            else:
                return render_template("checkout.html")
        else:
            return render_template("checkout.html")
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# This function is used to merge individual item arrays into the existing cart array
def array_merge(first_array, second_array):
    """
    function to merge cart items
    :param first_array: existing cart array
    :param second_array: user selected product's array
    :return: return merged cart array
    """
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


# Define the endpoint for adding a product into the database from the admin portal
@app.route("/add_product", methods=["POST"])
@login_required
def add_product():
    """
    Function allows admin to add a product into the database
    :return: returns to admin page with message about result of addition procedure.
    """
    try:
        if (
            not request.form.get("name")
            or not request.form.get("brand")
            or not request.form.get("price")
            or not request.form.get("image")
        ):
            flash("One of the mandatory fields not supplied")
            return redirect(url_for("admin"))
        product = Products(
            name=request.form.get("name"),
            brand=request.form.get("brand"),
            code=request.form.get("code"),
            price=request.form.get("price"),
            image=request.form.get("image"),
        )
        db.session.add(product)
        db.session.commit()
        flash(
            "Data for product with code {} has been added".format(
                request.form.get("code")
            )
        )
        return redirect(url_for("admin"))
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define the endpoint for deleting a product from the database from the admin portal
@app.route("/delete_product_data", methods=["POST"])
@login_required
def delete_product_data():
    """
    Function allows admin to delete a product from the database using the code as unique identifier
    :return: returns to admin page with message about result of deletion procedure.
    """
    try:
        if request.form.get("code"):
            product = Products.query.filter_by(code=request.form.get("code")).first()
            if product is not None:
                db.session.delete(product)
                db.session.commit()
                flash(
                    "Data for product with code {} has been deleted".format(
                        request.form.get("code")
                    )
                )
                return redirect(url_for("admin"))
            flash("Ooops.....Incorrect Code Supplied")
            return redirect(url_for("admin"))
        flash("You need to supply the product's code value to be able to delete it")
        return redirect(url_for("admin"))
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


# Define the endpoint for updating a product into the database from the admin portal
@app.route("/update_product", methods=["POST"])
@login_required
def update_product():
    """
    Function allows admin to update a product into the database using the code as unique identifier
    :return: returns to admin page with message about result of update procedure
    """
    try:
        if request.form.get("code"):
            if (
                not request.form.get("name")
                and not request.form.get("brand")
                and not request.form.get("price")
                and not request.form.get("image")
            ):
                flash("You need to supply at least one value to update apart from code")
                return redirect(url_for("admin"))
            product = Products.query.filter_by(code=request.form.get("code")).first()
            if request.form.get("name"):
                product.name = request.form.get("name")
            if request.form.get("brand"):
                product.brand = request.form.get("brand")
            if request.form.get("price"):
                product.price = request.form.get("price")
            if request.form.get("image"):
                product.image = request.form.get("image")
            db.session.commit()
            flash(
                "Data for product with code {} has been updated".format(
                    request.form.get("code")
                )
            )
            return redirect(url_for("admin"))
        flash(
            "You need to supply the product's code value to be able to update information"
        )
        return redirect(url_for("admin"))
    except Exception as e:
        print(
            "Oops....Unexpected error. Try reloading the page. Contact Site Administrator if it persists."
        )


"""
Run the app with the desired flags
ssl_context is used for specifying the path to the ssl certificate.
The "adhoc" parameter creates a dummy cert which enables us to use https
without buying a real certificate from a Certificate Authority.
This is only implemented for this academic exercise and we do not recommend
adopting this approach in any production environments.
Port flag can be used to specify different ports.
Debug can be enabled by setting to True for debugging purposes.
"""
if __name__ == "__main__":
    app.run(ssl_context="adhoc", port=int(config["flask"]["port"]), debug=False)
