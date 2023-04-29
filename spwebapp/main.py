# Import required modules
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

app = Flask(__name__)

# Define connection uri for your database
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mssql+pyodbc://root:root@localhost:1433/users_db?driver=ODBC Driver 17 for SQL Server"
app.config["SECRET_KEY"] = "abc"
app.static_folder = "./static"
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)
db = SQLAlchemy()


@app.after_request
def add_security_header(response):
    response.headers[
        "Content-Security-Policy"
    ] = "default-src 'none'; script-src 'self'; connect-src 'self'; img-src 'self'; style-src 'self'; frame-ancestors 'self'; form-action 'self';"
    response.headers["Server"] = "Not Gonna Tell Ya"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"
login_manager.login_message = "Please login to continue"
login_manager.login_message_category = "info"

csrf = CSRFProtect()
csrf.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    accesslevel = db.Column(db.String(5), default="user", nullable=False)
    isactive = db.Column(db.String(3), default="yes", nullable=False)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=False)


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.String(255), nullable=False)
    Address = db.Column(db.String(255), nullable=False)


db.init_app(app)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    user = Users.query.filter_by(id=session["_user_id"]).first()
    if user.accesslevel == "admin":
        try:
            product = Products.query.all()
            return render_template("admin.html", products=product)
        except Exception as e:
            print(e)
    else:
        return redirect(url_for("index"))


@app.route("/sign_up", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if (
            request.form.get("username")
            or request.form.get("password")
            or request.form.get("email")
        ):
            try:
                user = Users(
                    username=request.form.get("username"),
                    password=request.form.get("password"),
                    email=request.form.get("email"),
                )
                db.session.add(user)
                db.session.commit()
                flash("User Created. You can now log in")
                return redirect(url_for("login"))
            except Exception as e:
                flash("Exception Occured. Contact Administrator if this persists.")
                return redirect(url_for("register"))
        flash("one of the required fields is blank")
        return redirect(url_for("register"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") or request.form.get("password"):
            user = Users.query.filter_by(username=request.form.get("username")).first()
            if user is None:
                flash("Incorrect Username")
                return redirect(url_for("login"))
            if user.password == request.form.get("password"):
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
            return redirect(url_for("login"))
        flash("one of the required fields is blank")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out")
    return redirect(url_for("home"))


@app.route("/")
def default_path():
    return render_template("index.html")


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/orders")
@login_required
def orders():
    user = Users.query.filter_by(id=session["_user_id"]).first()
    if user.accesslevel == "fulfillment":
        try:
            total_orders = Orders.query.all()
            return render_template("orders.html", orders=total_orders)
        except Exception as e:
            print(e)
    else:
        return redirect(url_for("index"))


@app.route("/add", methods=["POST"])
@login_required
def add_product_to_cart():
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
        print(e)


@app.route("/shop", methods=["GET"])
@login_required
def shop():
    try:
        product = Products.query.all()
        return render_template("shop.html", products=product)
    except Exception as e:
        print(e)


@app.route("/empty")
@login_required
def empty_cart():
    try:
        session["cart_item"] = None
        return redirect(url_for("shop"))
    except Exception as e:
        print(e)


@app.route("/delete/<string:code>")
@login_required
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session["cart_item"].items():
            if item[0] == code:
                session["cart_item"].pop(item[0], None)
                if "cart_item" in session:
                    for key, value in session["cart_item"].items():
                        individual_quantity = int(session["cart_item"][key]["quantity"])
                        individual_price = float(
                            session["cart_item"][key]["total_price"]
                        )
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session["all_total_quantity"] = all_total_quantity
            session["all_total_price"] = all_total_price

        # return redirect('/')
        return redirect(url_for("shop"))
    except Exception as e:
        print(e)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart_load():
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


def array_merge(first_array, second_array):
    if isinstance(first_array, list) and isinstance(second_array, list):
        return first_array + second_array
    elif isinstance(first_array, dict) and isinstance(second_array, dict):
        return dict(list(first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance(second_array, set):
        return first_array.union(second_array)
    return False


@app.route("/add_product", methods=["POST"])
@login_required
def add_product():
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
        "Data for product with code {} has been added".format(request.form.get("code"))
    )
    return redirect(url_for("admin"))


@app.route("/delete_product_data", methods=["POST"])
@login_required
def delete_product_data():
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


@app.route("/update_product", methods=["POST"])
@login_required
def update_product():
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


if __name__ == "__main__":
    app.run(debug=True, port=8000)
