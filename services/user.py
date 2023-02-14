from entities.user import User
from models.user import UserSchema
from flask import jsonify
import pandas as pd
import jwt
from datetime import datetime, timedelta
import bcrypt
from Crypto.Random import get_random_bytes
from entities.databaseSessionManager import SessionManager

class UserCRUD():
    dbSession = SessionManager().session
    user_schemas = UserSchema(many=True)
    user_schema = UserSchema()
    key = 'missiningredient'
    iv =  get_random_bytes(16)

    def getUserList(self):
        user_list = self.dbSession.query(User).all()
        results = self.user_schemas.dump(user_list)
        return jsonify(results)
    
    def getUserByID(self,id):
        user = self.dbSession.query(User).get(id)
        return self.user_schema.jsonify(user)
    
    def encryptPassword(self,password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # raw = pad(raw.encode(),16)
        # cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC,self.iv)
        # return base64.b64encode(cipher.encrypt(raw)),base64.b64encode(cipher.iv).decode('utf-8')

    def decryptPassword(self,password,realpassword):
        return bcrypt.checkpw(password.encode('utf-8'), realpassword.encode('utf-8'))
        # enc = base64.b64decode(enc)
        # cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC,base64.b64decode(self.iv))
        # return unpad(cipher.decrypt(enc),16)
    
    def generateAccessToken(self,payload):
        jwt_token = jwt.encode(payload, self.key,algorithm='HS256')
        jwtDecoded = jwt_token.decode("utf-8")
        # self.createUserSession(payload.profileID, jwtDecoded)
        return jwtDecoded

    # def createUserSession(self, profileID, jwToken):
    #     userSession = UserSession(
    #         profileID = profileID,
    #         loggedOut = False,
    #         loginDate = datetime.now(),
    #         expireDate = datetime.now() + timedelta(hours=24), 
    #         jwToken=jwToken
    #     )
    #     self.dbSession.add(userSession)
    #     self.dbSession.commit()

    def login(self,email,password):
        user = self.dbSession.query(User).filter_by(email=email).first()
        password = self.decryptPassword(password,user.password)
        # password True or False geliyor
        payload = {
                'profileID': user.profileID,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(seconds=20)
            }
        # accessToken = self.generateAccessToken(payload)
        # print(accessToken)
        return self.user_schema.jsonify(user)

    def register(self,name,email,password,Age,Gender,MaritalStatus,Occupation):
        password = self.encryptPassword(password)
        user = User(name, email, password, Age,Gender,MaritalStatus,Occupation)
        self.dbSession.add(user)
        self.dbSession.commit()
        profileID = user.profileID
        userCSV = {
        'profileID':[profileID],
        'name': [name],
        'email': [email],
        'password': [password],
        'Age': [Age],
        'Gender':[Gender],
        'MaritalStatus':[MaritalStatus],
        'Occupation':[Occupation]
        }
        df = pd.DataFrame(userCSV)
        df.to_csv('users.csv', mode='a', index=False, header=False)        
        return self.user_schema.jsonify(user)
    
    def deleteUser(self,id): 
        user_list = pd.read_csv('users.csv')
        user = self.dbSession.query(User).get(id)
        self.dbSession.delete(user)
        self.dbSession.commit()
        user_list = user_list.drop(user_list[(user_list['profileID'] == int(id))].index)
        user_list.to_csv('users.csv', index=False)
        return self.user_schema.jsonify(user)
    
    def editUser(self,id,name,email,password,Age,Gender,MaritalStatus,Occupation):
        user_list = pd.read_csv('users.csv')
        password = self.encryptPassword(password)
        user = self.dbSession.query(User).get(id) 
        user.name = name
        user.email = email
        user.password = password
        user.Age = Age
        user.Gender = Gender
        user.MaritalStatus = MaritalStatus
        user.Occupation = Occupation
        self.dbSession.commit()
        
        index = user_list.index[user_list['profileID'] == int(id)].tolist()
        user_list.loc[index[0], 'name'] = name
        user_list.loc[index[0], 'email'] = email
        user_list.loc[index[0], 'password'] = password
        user_list.loc[index[0], 'Age'] = Age
        user_list.loc[index[0], 'Gender'] = Gender
        user_list.loc[index[0], 'MaritalStatus'] = MaritalStatus
        user_list.loc[index[0], 'Occupation'] = Occupation
        user_list.to_csv('users.csv', index=False)

        return self.user_schema.jsonify(user)
    
    
    # def logout(self,id):
    #     return id
    