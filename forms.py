from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.core import DecimalField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import InputRequired, Email


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    # TODO: make sure your validators here match the validators on the SQL level

class LoginForm(FlaskForm):
    """Form for registering a user."""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class CategorySelectionForm(FlaskForm):
    """Form for registering a user."""
    category = SelectField("Category", choices=[('Food & Drink', 'Food & Drink'), 
                                            ('Travel', 'Travel'), 
                                            ('Home Goods', 'Home Goods'),
                                            ('Apparel', 'Apparel'),
                                            ('Transportation', 'Transportation'),
                                            ('Housing', 'Housing'),
                                            ('Utilities', 'Utilities'),
                                            ('Miscellaneous', 'Miscellaneous')])

class ExpenseForm(FlaskForm):
    """Form for recording a expense"""
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired()])
    amount = DecimalField("Amount", validators=[InputRequired()])
    category = SelectField("Category", choices=[('Food & Drink', 'Food & Drink'), 
                                            ('Travel', 'Travel'), 
                                            ('Home Goods', 'Home Goods'),
                                            ('Apparel', 'Apparel'),
                                            ('Transportation', 'Transportation'),
                                            ('Housing', 'Housing'),
                                            ('Utilities', 'Utilities'),
                                            ('Miscellaneous', 'Miscellaneous')])

class CSRFOnlyForm(FlaskForm):
    """For CSRF protection only."""