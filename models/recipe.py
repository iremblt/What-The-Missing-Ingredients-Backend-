import flask
from flask_marshmallow import Marshmallow

app = flask.Flask(__name__)

SERVER = 'LAPTOP-7OGA62A2'
DATABASE = 'WhatTheMissingIngredientt'
DRIVER = 'SQL Server Native Client 11.0'
DATABASE_CONNECTION = f'mssql://{SERVER}/{DATABASE}?trusted_connection=yes&driver={DRIVER}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION

marsh = Marshmallow(app)
class RecipeSchema(marsh.Schema):
    class Meta:
        fields = ('Recipe_Name','Review_Count','Recipe_Photo','Author','Prepare_Time','Cook_Time','Total_Time','Ingredients','Directions','RecipeID')


class RecipeSchemaWithAvgRating(marsh.Schema):
    class Meta:
        fields = ('Recipe_Name','Review_Count','Recipe_Photo','Author','Prepare_Time','Cook_Time','Total_Time','Ingredients','Directions','RecipeID','RatingAvg')