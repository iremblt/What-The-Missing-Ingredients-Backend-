from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
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
