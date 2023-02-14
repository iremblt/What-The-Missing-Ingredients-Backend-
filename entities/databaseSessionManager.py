import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Run in terminal
#     >python
#     >>>from app import app
#     >>>from app import db
#     >>>db.create_all()

workingDirectory = os.getcwd()
configFile = os.path.join(workingDirectory, 'config.json')

with open(configFile, 'r') as jsonConfig:
    config = json.load(jsonConfig)

DATABASE_CONNECTION = config['DATABASE_CONNECTION']
engine = create_engine(DATABASE_CONNECTION, echo=True)

Session = sessionmaker(bind=engine)

class SessionManager(object):
    def __init__(self):
        self.session = Session()