import flask
from flask_marshmallow import Marshmallow

app = flask.Flask(__name__)

SERVER = 'LAPTOP-7OGA62A2'
DATABASE = 'WhatTheMissingIngredientt'
DRIVER = 'SQL Server Native Client 11.0'
DATABASE_CONNECTION = f'mssql://{SERVER}/{DATABASE}?trusted_connection=yes&driver={DRIVER}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION

marsh = Marshmallow(app)
class ReviewSchema(marsh.Schema):
    class Meta:
        fields = ('RecipeID','profileID','Rate','Comments','ReviewID')

class ReviewSchemaWithAuthorName(marsh.Schema):
    class Meta:
        fields = ('RecipeID','profileID','Rate','Comments','ReviewID','Author')