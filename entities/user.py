from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=False, nullable=False)
    Age = db.Column(db.Integer, unique=False, nullable=True)
    Gender = db.Column(db.String(10), unique=False, nullable=True)
    MaritalStatus = db.Column(db.String(50), unique=False, nullable=True)
    Occupation = db.Column(db.String(100), unique=False, nullable=True)
    profileID = db.Column(db.Integer, primary_key=True)

    def __init__(self,name,email,password,Age,Gender,MaritalStatus,Occupation):
        self.name = name
        self.email = email
        self.password = password
        self.Age = Age
        self.Gender = Gender
        self.MaritalStatus = MaritalStatus
        self.Occupation = Occupation
