from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db, User, Expense
from forms import RegisterForm, LoginForm, CSRFOnlyForm, ExpenseForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///personal_expense_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.get("/")
def homepage():
    """Redirects to the /register route."""
    return render_template("homepage.html")


#USER ROUTES
############################################################################################################
@app.get("/users/<username>")
def secret(username):
    """hidden page for logged-in users only."""

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        user = User.query.get_or_404(username)
        form = CSRFOnlyForm()

        return render_template("user_info.html", user=user, form=form)


@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage."""
    form = CSRFOnlyForm()

    if form.validate_on_submit():
        session.pop("username", None)

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        pwd = form.password.data

        user = User.register(
            username,
            pwd,
            email,
            first_name,
            last_name
        )
        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        return redirect(f"/users/{username}")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username, pwd)
        if user:
            session["username"] = user.username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)



#EXPENSE ROUTES
############################################################################################################

@app.route("/expenses/<username>/add", methods=["GET", "POST"])
def add_expense(username):
    """Produce login form or handle login."""

    form = ExpenseForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        amount = form.amount.data
        category = form.category.data
        user = username

        expense = Expense.create(name,description,amount,category,user)
        db.session.add(expense)
        db.session.commit()
        return redirect("/")

    else:
        return render_template("login.html", form=form)