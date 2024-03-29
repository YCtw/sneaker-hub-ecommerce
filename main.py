from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FormField
from flask_ckeditor import CKEditor, CKEditorField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from random import randint
import os
import pandas


# Basic setup
app = Flask(__name__)
app.secret_key = "SECRET_KEY"
ckeditor = CKEditor(app)
Bootstrap(app)

#Login setup
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return Members.query.get(int(user_id))

#Database setup
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///products.db"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#newProducts TABLE - create for heroku postgresql
class newProducts(db.Model):
    __tablename__ = "newproducts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(250), nullable=False)
    brand = db.Column(db.Text, nullable=False)

db.create_all()

#Member TABLE
class Members(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    birth = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)

db.create_all()

#Cart Table - contain all memebers' checkout which not ye been checkout
class Carts(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.Text, nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    product_size = db.Column(db.Text, nullable=False)
    product_count = db.Column(db.Integer, nullable=False)
    product_image_url = db.Column(db.Text, nullable=False)

db.create_all()

#Order Table - Confirmation, contain all orders' info
class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Text, nullable=False)
    buyer_id = db.Column(db.Integer, nullable=False)
    buyer_name = db.Column(db.Text, nullable=False)
    buyer_phone = db.Column(db.Text, nullable=False)
    buyer_email = db.Column(db.Text, nullable=False)
    buyer_address = db.Column(db.Text, nullable=False)
    order_note = db.Column(db.Text)

db.create_all()

#Direct Table - For direct purchase - not via cart checkout
class Directs(db.Model):
    __tablename__ = "directs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.Text, nullable=False)
    product_price = db.Column(db.Text, nullable=False)
    product_size = db.Column(db.Text, nullable=False)
    product_count = db.Column(db.Integer, nullable=False)
    product_image_url = db.Column(db.Text, nullable=False)
    order_status = db.Column(db.Text, nullable=False)

db.create_all()

#Bulding form for login
class LoginForm(FlaskForm):
    email = StringField(label="email", validators=[Email(message="Invalid email address"), DataRequired()] )
    password = PasswordField(label="password", validators=[DataRequired()])

#Bulding form for Register
class RegisterForm(FlaskForm):
    email = StringField(label="email", validators=[Email(message="Invalid email address"), DataRequired()])
    password = PasswordField(label="password", validators=[DataRequired()])
    first_name = StringField(label="first_name", validators=[DataRequired()])
    last_name = StringField(label="last_name", validators=[DataRequired()])
    phone = StringField(label="contact_phone", validators=[DataRequired()])
    address = StringField(label="address", validators=[DataRequired()])

#Bulding form for Credit card
class CardForm(FlaskForm):
    card_number = StringField(label="Card Number", validators=[DataRequired()])
    card_expired = StringField(label="Expired Date", validators=[DataRequired()])
    card_security = StringField(label="Security Code", validators=[DataRequired()])

#Bulding form for Checkout
class CheckoutForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired()])
    email = StringField(label="email", validators=[Email(message="Invalid email address"), DataRequired()])
    address = StringField(validators=[DataRequired()])
    c_card = FormField(CardForm)
    message = CKEditorField()

#Read items to postegresql db with csv - only do once, which is on first publish
# products_resource = pandas.read_csv("products.csv")
# name_list = products_resource["name"].tolist()
# price_list = products_resource["price"].tolist()
# url_list = products_resource["image_url"].tolist()
# category_list = products_resource["category"].tolist()
# brand_list = products_resource["brand"].tolist()
# for index in range(11):
#     product_row = newProducts(name=name_list[index], price=price_list[index], image_url=url_list[index], category=category_list[index], brand=brand_list[index])
#     db.session.add(product_row)
#     db.session.commit()

#Homepage
@app.route("/", methods=["GET", "POST"])
def homepage():
    #Store individual user's current product id and from_cart in session cookie
    session["current_product_id"] = 0
    session["from_cart"] = 0
    best_shoes = []
    normal_shoes = []
    all_shoes = db.session.query(newProducts).all()
    for shoe in all_shoes:
        if shoe.category == "best":
            best_shoes.append(shoe)
        else:
            normal_shoes.append(shoe)
    return render_template("index.html", best_shoes = best_shoes, normal_shoes=normal_shoes)

#Product page
@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    #Changing the product_id store in session to be the product user is currently looking at
    session["current_product_id"] = product_id

    item = newProducts.query.get(product_id)
    return render_template("product.html", item=item)

#Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    #Getting the indicator that if user is from cart
    from_cart = session.get("from_cart")
    login_form = LoginForm()
    #Post
    if login_form.validate_on_submit():
        #Getting the current_product_id from session to see where are users come in from
        current_product_id = session.get("current_product_id")
        login_email = login_form.email.data
        login_password = login_form.password.data
        search_email = Members.query.filter_by(email=login_email).first()
        if search_email == None:
            return render_template("login.html", form=login_form, fail_login = True)
        if search_email != None:
            correct_password = search_email.password
            if login_password == correct_password:
                if from_cart == 0:
                    if current_product_id == 0:
                        best_shoes = []
                        normal_shoes = []
                        all_shoes = db.session.query(newProducts).all()
                        for shoe in all_shoes:
                            if shoe.category == "best":
                                best_shoes.append(shoe)
                            else:
                                normal_shoes.append(shoe)
                        login_user(search_email)
                        return render_template("index.html", best_shoes=best_shoes, normal_shoes=normal_shoes, successfully_login= True)
                    elif current_product_id != 0:
                        item = newProducts.query.get(current_product_id)
                        login_user(search_email)
                        return render_template("product.html", item=item)
                if from_cart == 1:
                    login_user(search_email)
                    session["from_cart"] = 0 #把session裡面的from_cart還原成0
                    return redirect(url_for("cart"))
            if login_password != correct_password:
                return render_template("login.html", form=login_form, fail_login = True)

    #Get
    true_product_id = request.args.get("product_id")# From homepage or From product page
    if true_product_id != None:
        true_product_id = int(true_product_id)
    if true_product_id == 0:
        session["current_product_id"] = 0
    return render_template("login.html", form=login_form)

#Register page
@app.route("/register", methods=["GET","POST"])
def register():
    register_form = RegisterForm()
    #Post
    if register_form.validate_on_submit():
        email = register_form.email.data
        password =register_form.password.data
        first_name = register_form.first_name.data
        last_name = register_form.last_name.data
        birth = request.form["birth"]
        phone = register_form.phone.data
        address = register_form.address.data
        duplicate_email = Members.query.filter_by(email=email).first()
        if duplicate_email != None:
            return render_template("register.html", form=register_form, duplicate_email=True)
        else:
            new_register = Members(first_name = first_name, last_name=last_name, email=email, password=password, birth=birth, phone=phone, address=address)
            db.session.add(new_register)
            db.session.commit()
            return redirect(url_for("login"))

    #Get
    return render_template("register.html", form=register_form)

#Logout
@app.route("/logout", methods=["GET"])
def logout():
    current_product_id = session.get("current_product_id")
    logout_user()
    if current_product_id == 0:
        return redirect(url_for("homepage"))
    elif current_product_id != 0:
        item = newProducts.query.get(current_product_id)
        return render_template("product.html", item=item)

#Cart page
@app.route("/cart", methods=["GET","POST"])
def cart():
    current_product_id = session.get("current_product_id")
    from_cart = session.get("from_cart")
    #From cart or from register, login
    if request.method == "GET":
        if current_user.is_authenticated == False:
            session["from_cart"] = 1
            return redirect(url_for("login"))
        elif current_user.is_authenticated:
            current_user_id = current_user.id
            current_user_id_cart_product = Carts.query.filter_by(user_id=current_user_id).all()
            if len(current_user_id_cart_product) == 0:
                return render_template("cart.html", is_empty=True)
            elif len(current_user_id_cart_product) != 0:
                sum_cart_price = 0
                for cart_item in current_user_id_cart_product:
                    sum_cart_price = sum_cart_price + (cart_item.product_price* cart_item.product_count)
                last_element = len(current_user_id_cart_product) - 1
                return render_template("cart.html", cart_list = current_user_id_cart_product, sum_price = sum_cart_price, is_empty=False, last_element=last_element)
    if request.method == "POST":
        if current_user.is_authenticated:
            item_to_cart = newProducts.query.get(current_product_id)
            #search for the same user and same item in the current cart db first
            current_cart_result = Carts.query.filter_by(user_id = current_user.id).all()
            for current_product in current_cart_result:
                if current_product.product_id == current_product_id and current_product.product_size == request.form["size"]:
                    current_product.product_count = current_product.product_count + int(request.form["count"])
                    db.session.commit()
                    return redirect(url_for("product", product_id=current_product_id))
            user_id = current_user.id
            product_name = item_to_cart.name
            product_id = item_to_cart.id
            product_price = item_to_cart.price
            product_url = item_to_cart.image_url
            product_size = request.form["size"]
            product_count = request.form["count"]
            add_to_cart_row = Carts(user_id=user_id, product_id=product_id, product_name=product_name, product_price=product_price, product_size=product_size, product_count=product_count, product_image_url=product_url)
            db.session.add(add_to_cart_row)
            db.session.commit()
            return redirect(url_for("product", product_id=product_id))
        #還沒登入但想加購物車，先去登入
        else:
            return redirect(url_for("login"))

#Delete cart
@app.route("/delete", methods=["GET"])
def delete():
    delete_id = request.args.get('delete_id')
    delete_target = Carts.query.get(delete_id)
    db.session.delete(delete_target)
    db.session.commit()
    return redirect(url_for("cart"))

#Checkout page
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    current_product_id = session.get("current_product_id")
    checkout_form = CheckoutForm()
    real_checkout_post = request.args.get("purchase")
    #直接購買
    if request.method == "POST" and real_checkout_post == 'direct':
        if current_user.is_authenticated:
            item_to_cart = newProducts.query.get(current_product_id)
            user_id = current_user.id
            product_name = item_to_cart.name
            product_id = item_to_cart.id
            product_price = item_to_cart.price
            product_url = item_to_cart.image_url
            product_size = request.form["size"]
            product_count = int(request.form["count"])

            #Check user's previous progress/finish direct item, just delete it
            previous_direct_finish_item = Directs.query.filter_by(user_id=user_id, order_status="finish").all()
            previous_direct_progress_item = Directs.query.filter_by(user_id=user_id, order_status="progress").all()
            if previous_direct_finish_item != None:
                for p_item in previous_direct_finish_item:
                    print(p_item.product_name)
                    db.session.delete(p_item)
                    db.session.commit()
            if previous_direct_progress_item != None:
                for d_item in previous_direct_progress_item:
                    db.session.delete(d_item)
                    db.session.commit()

            #Adding direct purchase to database, with status "progress"
            new_direct_purchase = Directs(user_id=user_id, product_id=product_id, product_name=product_name, product_price=product_price, product_size=product_size, product_count=product_count, product_image_url=product_url, order_status="progress")
            db.session.add(new_direct_purchase)
            db.session.commit()

            direct_item = Directs.query.filter_by(user_id=user_id, order_status="progress").first()
            sum_price = product_price * product_count
            return render_template("checkout.html", checkout_form=checkout_form, direct_item=direct_item, direct=True, sum_price=sum_price)
        else:
            return redirect(url_for("login"))
    #購物車結帳
    elif request.method == "GET":
        current_user_id = current_user.id
        current_user_id_cart_product = Carts.query.filter_by(user_id=current_user_id).all()
        sum_checkout_price = 0
        for cart_item in current_user_id_cart_product:
            sum_checkout_price = sum_checkout_price + (cart_item.product_price * cart_item.product_count)
        return render_template("checkout.html", checkout_form = checkout_form, checkout_list = current_user_id_cart_product, sum_price = sum_checkout_price)

#Confirmation page
@app.route("/confirmation", methods=["GET","POST"])
def confirmation():
    # direct_confirm_dict = session.get("direct_purchase")
    # print(direct_confirm_dict)
    checkout_form = CheckoutForm()
    from_direct = request.args.get("direct")
    if request.method == "POST" and from_direct == "No":
        direct_condition = False
        checkout_name = checkout_form.name.data
        checkout_phone = checkout_form.phone.data
        checkout_email = checkout_form.email.data
        checkout_address = checkout_form.address.data
        message = checkout_form.message.data
        #Validate not working, so if it's empty then use user's register information
        if checkout_name == "":
            checkout_name = current_user.first_name + " " + current_user.last_name
        if checkout_phone == "":
            checkout_phone = current_user.phone
        if checkout_email == "":
            checkout_email = current_user.email
        if checkout_address == "":
            checkout_address = current_user.address
        order_name = "A"
        for _ in range(5):
            order_name  = order_name + str(randint(0,10))
        new_orders = Orders(order_id=order_name, buyer_id = current_user.id, buyer_name = checkout_name, buyer_phone = checkout_phone, buyer_email = checkout_email, buyer_address = checkout_address, order_note=message)
        db.session.add(new_orders)
        db.session.commit()
        user_checkout_list = Carts.query.filter_by(user_id = current_user.id).all()
        #Delete from carts after checkout
        for done_item in user_checkout_list:
            db.session.delete(done_item)
            db.session.commit()
        new_orders_info = Orders.query.filter_by(order_id = order_name).first()
        return render_template("confirmation.html", user_checkout_list=user_checkout_list, confirm_order=new_orders_info, from_direct=direct_condition)

    if request.method == "POST" and from_direct == "Yes":
        direct_condition = True
        checkout_name = checkout_form.name.data
        checkout_phone = checkout_form.phone.data
        checkout_email = checkout_form.email.data
        checkout_address = checkout_form.address.data
        message = checkout_form.message.data
        # Validate not working, so if it's empty then use user's register information
        if checkout_name == "":
            checkout_name = current_user.first_name + " " + current_user.last_name
        if checkout_phone == "":
            checkout_phone = current_user.phone
        if checkout_email == "":
            checkout_email = current_user.email
        if checkout_address == "":
            checkout_address = current_user.address
        order_name = "A"
        for _ in range(5):
            order_name = order_name + str(randint(0, 10))
        new_orders = Orders(order_id=order_name, buyer_id=current_user.id, buyer_name=checkout_name,buyer_phone=checkout_phone, buyer_email=checkout_email, buyer_address=checkout_address, order_note=message)
        db.session.add(new_orders)
        db.session.commit()
        new_orders_info = Orders.query.filter_by(order_id=order_name).first()

        direct_item = Directs.query.filter_by(user_id=current_user.id, order_status="progress").first()
        direct_sum = direct_item.product_price*direct_item.product_count

        #Changing the status in direct db to finish so it won't get include in next visit
        direct_item.order_status = "finish"
        db.session.commit()
        return render_template("confirmation.html", direct_item=direct_item,  direct_sum=direct_sum, confirm_order=new_orders_info, from_direct=direct_condition)

if __name__ == "__main__":
    app.run(debug=True)
