
# Import required modules
from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
# Define connection uri for your database
app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://root:root@localhost:1433/users_db?driver=ODBC Driver 17 for SQL Server"
app.config["SECRET_KEY"] = "abc"
app.static_folder = "./static"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"
login_manager.login_message = "Please login to continue"
login_manager.login_message_category = "info"

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

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

db.init_app(app)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)


@app.route('/admin', methods=["GET", "POST"])
def admin():
    try:
        product = Products.query.all()
        return render_template("admin.html", products=product)
    except Exception as e:
        print(e)


@app.route('/sign_up', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # user = Users(username=request.form.get("username"),password=request.form.get("password"))
        user = Users(username=request.form.get("username"), password=request.form.get("password"), email=request.form.get("email"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if user.password == request.form.get("password") and user.isactive == "yes":
            login_user(user)
            if user.accesslevel == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for('home'))
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
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


@app.route('/add', methods=['POST'])
@login_required
def add_product_to_cart():
    try:
        _quantity = int(request.form['quantity'])
        _code = request.form['code']
        # validate the received values
        if _quantity and _code and request.method == 'POST':
            product_list = Products.query.all()
            for product in product_list:
                if product.code == _code:
                    product_value = product
                    break
            product =product_value
            itemArray = {
                product.code: {'name': product.name, 'code': product.code, 'quantity': _quantity, 'price': product.price,
                              'image': product.image, 'total_price': _quantity * product.price}}

            all_total_price = 0
            all_total_quantity = 0
            session.modified = True
            if 'cart_item' in session:
                if session['cart_item'] is not None:
                    if product.code in session['cart_item']:
                        for key, value in session['cart_item'].items():
                            if product.code == key:
                                # session.modified = True
                                # if session['cart_item'][key]['quantity'] is not None:
                                #	session['cart_item'][key]['quantity'] = 0
                                old_quantity = session['cart_item'][key]['quantity']
                                total_quantity = old_quantity + _quantity
                                session['cart_item'][key]['quantity'] = total_quantity
                                session['cart_item'][key]['total_price'] = total_quantity * product.price
                    else:
                        session['cart_item'] = array_merge(session['cart_item'], itemArray)

                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                else:
                    session['cart_item'] = itemArray
                    all_total_quantity = all_total_quantity + _quantity
                    all_total_price = all_total_price + _quantity * product.price
            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * product.price

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price
            return redirect(url_for('shop'))
        else:
            return 'Error while adding item to cart'
    except Exception as e:
        print(e)



@app.route('/shop', methods=["GET"])
@login_required
def shop():
    try:
        product = Products.query.all()
        return render_template('shop.html', products=product)
    except Exception as e:
        print(e)


@app.route('/empty')
@login_required
def empty_cart():
    try:
        session['cart_item'] = None
        return redirect(url_for('shop'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
@login_required
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/')
        return redirect(url_for('shop'))
    except Exception as e:
        print(e)


@app.route('/cart', methods=["GET", "POST"])
@login_required
def cart_load():
    if request.method == "POST":
        print("done")
        # execute db query to store form info with username date and order status/id
    total_items = []
    if 'cart_item' in session:
        if session['cart_item'] is not None:
            for item in (session['cart_item']).keys():
                total_items.append(session['cart_item'][item])
            total_items_count = len(total_items)
            return render_template("checkout.html", total_items=total_items, total_items_count=total_items_count)
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


if __name__ == "__main__":
    app.run(debug=True, port=8000)
