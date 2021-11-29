from datetime import datetime
from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension

from models import connect_db, db, User, Expense
from forms import CategorySelectionForm, RegisterForm, LoginForm, CSRFOnlyForm, ExpenseForm

from helpers import sum_expenses, calculate_stats_for_category

from sqlalchemy import extract

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

    if "username" in session:
        return redirect(f"/summary/{session['username']}")
    else:
        return render_template("homepage.html", logout_form=logout_form)


#USER ROUTES
############################################################################################################
@app.get("/users/<username>")
def user_detail(username):
    """hidden page for logged-in users only."""

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        user = User.query.get_or_404(username)
        logout_form = CSRFOnlyForm()

        todays_month=datetime.now().month
        expenses_query_data = db.session.query(Expense.category, db.func.sum(Expense.amount)).filter((extract('month',Expense.time_added) == todays_month)).group_by(Expense.category).all()
        expenses = dict(expenses_query_data)


        if expenses == {}:
            total_expenses = 0
        else:
            total_expenses = sum_expenses(expenses)

        return render_template("user_info.html", user=user, 
                                                logout_form=logout_form,
                                                total_expenses=total_expenses)


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
    
    user = User.query.get_or_404(username)

    if username != user.username:
        flash("Invalid credentials")
        return redirect(f"/users/{username}")

    else:
        logout_form=CSRFOnlyForm()
        form=CategorySelectionForm()
        todays_month=datetime.now().month
        # get list of all the expenses for a given user
        expenses_query_data = db.session.query(Expense.category, db.func.sum(Expense.amount)).filter((extract('month',Expense.time_added) == todays_month)).group_by(Expense.category).all()

        # make expenses a dictionary which can be passed to a template
        expenses = dict(expenses_query_data)

        if expenses == {}:
            total_expenses = 0
        else:
            total_expenses = sum_expenses(expenses)
        

        # get the selected category
        selected_category = request.args.get('category')

        # grab the category expenses, and get the list of amounts
        category_expense_query_data = Expense.query.filter((Expense.owner == username),(Expense.category == selected_category),(extract('month',Expense.time_added) == todays_month)).all()
        category_expenses = [e.amount for e in category_expense_query_data]

        category_stats= calculate_stats_for_category(category_expenses)
        
        return render_template("expense_summary.html", 
                                total_expenses=total_expenses,
                                expenses=expenses,
                                logout_form=logout_form,
                                form=form, 
                                selected_category=selected_category,
                                category_stats=category_stats)
