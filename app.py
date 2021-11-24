from datetime import datetime
from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db, User, Expense
from forms import CategorySelectionForm, RegisterForm, LoginForm, CSRFOnlyForm, ExpenseForm

from sqlalchemy import extract

import functools

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
    logout_form = CSRFOnlyForm()

    return render_template("homepage.html", logout_form=logout_form)


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
        logout_form = CSRFOnlyForm()

        return render_template("user_info.html", user=user, logout_form=logout_form)


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
    logout_form=CSRFOnlyForm()


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
        return render_template("register.html", form=form,logout_form=logout_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()
    logout_form=CSRFOnlyForm()


    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username, pwd)
        if user:
            session["username"] = user.username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form,logout_form=logout_form)



#EXPENSE ROUTES
############################################################################################################

@app.route("/expenses/<username>/add", methods=["GET", "POST"])
def add_expense(username):
    """Produce login form or handle login."""
        
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    form = ExpenseForm()
    logout_form=CSRFOnlyForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        amount = form.amount.data
        category = form.category.data

        breakpoint()
        # expense = Expense.create(name,description,amount,category,user)
        expense = Expense.create(name,description,amount,category)
        db.session.add(expense)
        db.session.commit()
        return redirect("/")

    else:
        return render_template("add_expense.html", logout_form=logout_form,form=form)

@app.get("/summary/<username>")
def expense_summary(username):
    """hidden page for logged-in users only."""

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        logout_form=CSRFOnlyForm()
        form=CategorySelectionForm()
        todays_month=datetime.now().month
        # get list of all the expenses for a given user
        expenses_query_data = Expense.query.filter((Expense.owner == username),(extract('month',Expense.time_added) == todays_month)).all()

        breakpoint()
        # make expenses a dictionary of each type rather than a sum of the totals in an array.
        # then we can still handle this the same way but do it by reducing a dictionary rather than a list
        # here is a stack overflow on how to reduce a dictionary
        # to get first expense, it would be expenses[0].category:expenses[0].amount 

        # boil them down to just their amounts
        expenses = [e.amount for e in expenses_query_data]
        # get total

        if expenses == []:
            total_expenses = 0
        else:
            total_expenses = functools.reduce(lambda a, b: a+b, expenses)
        
        # get the selected category
        selected_category = request.args.get('category')

        # grab the category expenses, and get the list of amounts
        category_expense_query_data = Expense.query.filter((Expense.owner == username),(Expense.category == selected_category),(extract('month',Expense.time_added) == todays_month)).all()
        category_expenses = [e.amount for e in category_expense_query_data]

        # if that list is empty, set total to 0. Otherwise, get the sum
        if category_expenses == []:
            total_category_expenses=0
        else:
            total_category_expenses = functools.reduce(lambda a, b: a+b, category_expenses)

        return render_template("expense_summary.html", 
                                total_expenses=total_expenses,
                                logout_form=logout_form,
                                form=form, 
                                selected_category=selected_category,
                                total_category_expenses=total_category_expenses)
