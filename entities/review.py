from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Review(db.Model):
    __tablename__ = 'clean_reviews'
    RecipeID = db.Column(db.Integer, unique=False, nullable=False)
    profileID = db.Column(db.Integer, unique=False, nullable=False)
    Rate = db.Column(db.Float, unique=False, nullable=False)
    Comments = db.Column(db.String(5000), unique=False, nullable=True)
    ReviewID = db.Column(db.Integer, primary_key=True)

    def __init__(self,RecipeID,profileID,Rate,Comments):
        self.RecipeID = RecipeID
        self.profileID = profileID
        self.Rate = Rate
        self.Comments = Comments
