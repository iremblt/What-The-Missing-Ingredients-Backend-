from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json
import os
import pandas as pd
import pyodbc   
from entities.databaseSessionManager import SessionManager
from entities.recipe import Recipe
import string
from services.recipe import RecipeCRUD
from services.user import UserCRUD

app = Flask(__name__)

recipe_list = pd.read_csv('clean_recipes.csv', delimiter=';')
recipe_list = recipe_list.fillna(0)
conn_str = (
    r'DRIVER={SQL Server Native Client 11.0};'
    r'SERVER=LAPTOP-7OGA62A2;'
    r'DATABASE=WhatTheMissingIngredientt;'
    r'Trusted_Connection=yes;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS clean_recipes;')
cursor.execute("CREATE TABLE clean_recipes (Recipe_Name varchar(250),Review_Count varchar(100),Recipe_Photo varchar(250),Author varchar(100),Prepare_Time varchar(100),Cook_Time varchar(100),Total_Time varchar(100),Ingredients varchar(max),Directions varchar(max),RecipeID int IDENTITY(1, 1) PRIMARY KEY)")

cursor.execute("SET IDENTITY_INSERT dbo.clean_recipes ON")
for row in recipe_list.itertuples():
    cursor.execute(
            '''
            INSERT INTO WhatTheMissingIngredientt.dbo.clean_recipes(Recipe_Name,Review_Count,Recipe_Photo,Author,Prepare_Time,Cook_Time,Total_Time,Ingredients,Directions,RecipeID)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            ''',
            row[1], 
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10]
    )
conn.commit()
cursor.execute("SET IDENTITY_INSERT dbo.clean_recipes OFF")

reviews_list = pd.read_csv('clean_reviews.csv')
reviews_comments = pd.read_csv('reviews.csv',  sep=';', encoding='cp1252', error_bad_lines=False,low_memory=False)
reviews_list['ReviewID']=reviews_list.index
reviews_list['Comments'] = reviews_comments['Comment']
reviews_list.to_csv('clean_reviews.csv', index=False)
reviews_list = reviews_list.fillna(0)
cursor.execute('DROP TABLE IF EXISTS clean_reviews;')
cursor.execute("CREATE TABLE clean_reviews (RecipeID int,profileID int, Rate float, ReviewID int IDENTITY(1, 1) PRIMARY KEY,Comments varchar(max))")
cursor.execute("SET IDENTITY_INSERT dbo.clean_reviews ON")
for row in reviews_list.itertuples():
    cursor.execute(
            '''
            INSERT INTO WhatTheMissingIngredientt.dbo.clean_reviews(RecipeID,profileID,Rate,ReviewID,Comments)
            VALUES(?,?,?,?,?)
            ''',
            row[1], 
            row[2],
            row[3],
            row[4],
            row[5]
    )
conn.commit()
cursor.execute("SET IDENTITY_INSERT dbo.clean_reviews OFF")

user_list = pd.read_csv('users.csv')
# user_list['user_id']= reviews_list['profileID']
# user_list.pop('Educational Qualifications')
# user_list.pop('Family size')
# user_list.pop('Unnamed: 0')
# user_list.pop('Monthly Income')
# user_list.rename(columns={"user_id": "profileID"}, inplace=True)
user_list.drop_duplicates(subset="profileID",keep=False, inplace=True)
user_list.to_csv('users.csv', index=False)
cursor.execute('DROP TABLE IF EXISTS users;')
cursor.execute("CREATE TABLE users (profileID int IDENTITY(1, 1) PRIMARY KEY,name varchar(120),email varchar(250),password varchar(150),Age int,Gender varchar(10),MaritalStatus varchar(50),Occupation varchar(100))")
cursor.execute("SET IDENTITY_INSERT dbo.users ON")
for row in user_list.itertuples():
    cursor.execute(
            '''
            INSERT INTO WhatTheMissingIngredientt.dbo.users(profileID,name,email,password,Age,Gender,MaritalStatus,Occupation)
            VALUES(?,?,?,?,?,?,?,?)
            ''',
            row[1], 
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8]
    )
conn.commit()
cursor.execute("SET IDENTITY_INSERT dbo.users OFF")

workingDirectory = os.getcwd()
configFile = os.path.join(workingDirectory, 'config.json')

with open(configFile, 'r') as jsonConfig:
    config = json.load(jsonConfig)
DATABASE_CONNECTION = config['DATABASE_CONNECTION']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION
app.app_context().push()

db = SQLAlchemy(app)

class Recipe(db.Model):
    __tablename__ = 'clean_recipes'
    Recipe_Name = db.Column(db.String(250), unique=False,nullable=False)
    Review_Count = db.Column(db.String(250), unique=False,nullable=True)
    Recipe_Photo = db.Column(db.String(250), unique=False, nullable=False)
    Author = db.Column(db.String(120), unique=False, nullable=False)
    Prepare_Time = db.Column(db.String(120), unique=False, nullable=True)
    Cook_Time = db.Column(db.String(120), unique=False, nullable=True)
    Total_Time = db.Column(db.String(120), unique=False, nullable=True)
    Ingredients = db.Column(db.String(5000), unique=False, nullable=False)
    Directions = db.Column(db.String(5000), unique=False, nullable=True)
    RecipeID = db.Column(db.Integer, primary_key=True)
    def __init__(self,Recipe_Name,Review_Count,Recipe_Photo,Author,Prepare_Time,Cook_Time,Total_Time,Ingredients,Directions):
        self.Recipe_Name = Recipe_Name
        self.Review_Count = Review_Count
        self.Recipe_Photo = Recipe_Photo
        self.Author = Author
        self.Prepare_Time = Prepare_Time
        self.Cook_Time = Cook_Time
        self.Total_Time = Total_Time
        self.Ingredients = Ingredients
        self.Directions = Directions

class Review(db.Model):
    __tablename__ = 'clean_reviews'
    RecipeID = db.Column(db.Integer, unique=False, nullable=False)
    profileID = db.Column(db.Integer, unique=False, nullable=False)
    Rate = db.Column(db.Float, unique=False, nullable=False)
    Comments = db.Column(db.String(5000), unique=False, nullable=True)
    ID = db.Column(db.Integer, primary_key=True)
    def __init__(self,RecipeID,profileID,Rate,Comments):
        self.RecipeID = RecipeID
        self.profileID = profileID
        self.Rate = Rate
        self.Comments = Comments

class User(db.Model):
    __tablename__ = 'users'
    name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
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


dbSession = SessionManager().session
recipeServices = RecipeCRUD()
userServices = UserCRUD()

recipe_list = dbSession.query(Recipe)
authors = []
translator = str.maketrans('', '', string.punctuation)
for recipe in recipe_list.all():
    if recipe.Author.lower() not in authors:
        authors.append(recipe.Author.lower())
        forEmail = recipe.Author.translate(translator)
        email = forEmail.replace(' ',"").lower() + "@hotmail.com"
        password = recipe.Author.replace(' ',"") +"T1?ks."
        created_user_response =  userServices.createForRecipe(recipe.Author,email,password,30,'Female','Single','Chef')
        find_active_recipes = recipe_list.filter_by(Author=recipe.Author.lower()).all() or recipe_list.filter_by(Author=recipe.Author).all()
        for recipe in find_active_recipes:
            recipeServices.editRecipe(recipe.RecipeID,recipe.Recipe_Name, recipe.Review_Count, recipe.Recipe_Photo, str(created_user_response.profileID), recipe.Prepare_Time, recipe.Cook_Time,recipe.Total_Time,recipe.Ingredients,recipe.Directions)

other_authors = ['VINCE JONES','DAISY','MIKE','VICKI','NATALIE L','MICHELLE','KIM','JODI','MELODIE','KIM NIEDERREITHER','ANGIE V.','DENISE SMITH','JUDITH','LAURIE NANNI','CRAIG']
for author in other_authors:
    forEmail = author.translate(translator)
    email = forEmail.replace(' ',"").lower() + "@hotmail.com"
    password = author.replace(' ',"") +"T1?ks."
    find_active_recipes = recipe_list.filter_by(Author=author.lower()).all() or recipe_list.filter_by(Author=author).all()
    created_user_response =  userServices.createForRecipe(author,email,password,30,'Female','Single','Chef')
    for recipe in find_active_recipes:
        recipeServices.editRecipe(recipe.RecipeID,recipe.Recipe_Name, recipe.Review_Count, recipe.Recipe_Photo, str(created_user_response.profileID), recipe.Prepare_Time, recipe.Cook_Time,recipe.Total_Time,recipe.Ingredients,recipe.Directions)

db.create_all()
db.session.commit()