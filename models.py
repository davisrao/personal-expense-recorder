from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from enum import Enum

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class CategoryOptions(Enum):
    FOOD = 'Food & Drink'
    TRAVEL = 'Travel'
    HOME = 'Home Goods'
    APPAREL = 'Apparel'
    TRANSPORTATION = 'Transportation'
    HOUSING = 'Rent / Housing'
    UTILITIES = 'Utilities'
    INSURANCE = 'Insurance'
    MISC = 'Miscellaneous'


class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    username = db.Column(
        db.String(20),
        primary_key=True
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.String(30),
        nullable=False
    )
    
    last_name = db.Column(
        db.String(30),
        nullable=False
    )

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/ hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd).decode('utf8')

        return cls(
            username=username, 
            password=hashed, 
            email=email, 
            first_name=first_name, 
            last_name=last_name
        )
        # NOTE: Could do the db.session.add() here

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = cls.query.get(username)

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False


class Expense(db.Model):
    """Expense class"""

    __tablename__ = "expenses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
    db.String(300),
    nullable=False
)

    description = db.Column(
        db.String(300),
        nullable=False
    )

    amount = db.Column(
        db.Integer,
        nullable=False
    )

    category = db.Column(db.Enum(CategoryOptions,
                                values_callable=lambda x: 
                                [str(member.value) for member in CategoryOptions]))
    owner = db.Column(
        db.String(20),
        db.ForeignKey('users.username')
    )

    user = db.relationship('User',
                            backref='expenses')
    @classmethod
    def create(cls, name, description, amount, category):
        """Register expense in the database w/"""

        return cls(
            name=name, 
            description=description, 
            amount=amount, 
            category=category, 
        )