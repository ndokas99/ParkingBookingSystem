from flask import Flask, flash, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
from re import search

settings = {
    "SECRET_KEY": '64D5B6GB546BD4FBD49R8DG65BD',
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///Database.db',
    "SQLALCHEMY_TRACK_MODIFICATIONS": False
}

app = Flask(__name__)
app.debug = True
app.config.update(settings)
db = SQLAlchemy(app)


class Acc(db.Model):
    idNumber = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    surname = db.Column(db.Text, nullable=False)
    gender = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=True)
    password = db.Column(db.Text, nullable=False)
    zone = db.Column(db.Text, nullable=True)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contact = db.Column(db.Text, nullable=True)
    message = db.Column(db.String, nullable=False)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        idNum = request.form['idNum'].replace(" ", "").replace("-", "")
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        gender = request.form['gender']
        phone = request.form['phone'].replace(" ", "")
        password1 = request.form['password1']
        password2 = request.form['password2']

        if Acc.query.filter_by(idNumber=idNum).first():
            flash("Account with this ID already exists")
        elif not search(r".*?@.*?[.]com", email):
            flash("Email is invalid", category="error")
        elif email.count(" ") > 0:
            flash("Email should not contain spaces", category="error")
        elif not search(r"[+263][0-9]*|07[0-9]*", phone) or search(r"[a-zA-Z]", phone):
            flash("Invalid phone number", category="error")
        elif password1 != password2:
            flash("Passwords do not match", category="error")
        elif not gender:
            flash("Gender field should not be blank", category="error")
        elif len(password1) < 5:
            flash("Passwords should be at least 5 characters", category="error")
        else:
            acc = Acc(idNumber=idNum,
                      name=name,
                      surname=surname,
                      gender=gender,
                      phone=phone,
                      email=email,
                      password=generate_password_hash(password1)
                      )
            db.session.add(acc)
            db.session.commit()
            flash("Account created successfully.", category="success")
            return render_template("userLogin.html")

        return render_template("register.html")


@app.route('/userLogin')
def userLogin():
    return render_template("userLogin.html")


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        idNum = request.form['idNum'].replace(" ", "").replace("-", "")
        password = request.form['password']

        acc = Acc.query.filter_by(idNumber=idNum).first()
        if acc:
            if check_password_hash(acc.password, password):
                session['id'] = idNum
                return redirect("book")
            else:
                flash("Password invalid", category="error")
        else:
            flash("Account does not exist", category="error")

        return render_template("userLogin.html")


@app.route('/help')
def help_():
    return render_template("help.html")


@app.route('/feedback', methods=['POST'])
def feedback():
    if request.method == 'POST':
        feed = Feedback(contact=request.form['contact'],
                        message=request.form['msg'])
        db.session.add(feed)
        db.session.commit()
        flash("Feedback message send successfully", category="success")
        return render_template("help.html")


@app.route('/adminLogin')
def admin():
    return render_template("adminLogin.html")


@app.route('/cpbs', methods=['POST'])
def cpbs():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "cpbs":
            accs = Acc.query.all()
            feeds = Feedback.query.all()
            return render_template("cpbs.html", accs=accs, feeds=feeds)
        else:
            flash("Access denied", category="error")
            return render_template("adminLogin.html")


@app.route('/book')
def book():
    return render_template("book.html")


@app.route('/bookZone', methods=['POST'])
def bookZone():
    if request.method == 'POST':
        zone = request.form['zone']
        acc = Acc.query.filter_by(idNumber=session['id']).first()
        acc.zone = zone
        db.session.commit()
        flash(f"Booked successfully in {zone}. You will be allocated a parking spot when you arrive.", category="success")
        return render_template("index.html")


def create_database():
    if not path.exists("Database.db"):
        db.create_all()


if __name__ == '__main__':
    with app.app_context():
        create_database()
        app.run("0.0.0.0")
