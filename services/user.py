from entities.user import User
from models.user import UserSchema
from flask import jsonify
import jwt
import re
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
        ## recipe ları getir
        ## recipe ların author name lerini bi yere yaz eğer içeriyorsa bu liste de ekleme
        ## her bir author için user pass email vs oluştur ve post at 
        ## post attıktan sonra gelen profileID'i recipe a ekle ??
        ## recipe da profileID diye bir kısım yok yeni bir column oluştur recipe da ??
        user_list = self.dbSession.query(User).all()
        if len(user_list) == 0 :
            message = 'There is no user yet. You need to register it'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            message = 'Successfully listed all users'
            results = self.user_schemas.dump(user_list)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
    
    def getUserByID(self,id):
        user = self.dbSession.query(User).get(id)
        if user :
            message = 'Successfully detailed this user'
            response = self.user_schema.jsonify(user)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no user for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
    
    def encryptPassword(self,password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def decryptPassword(self,password,realpassword):
        return bcrypt.checkpw(password.encode('utf-8'), realpassword.encode('utf-8'))
    
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
        error = self.validateUser(email,password,status='login')
        if error is 'None':
            user = self.dbSession.query(User).filter_by(email=email).first()
            if user is None:
                jsonify({'message':'There is no user','success':'404 NOT FOUND'})
            else:
                password = self.decryptPassword(password,user.password)
                if password is False:
                    jsonify({'message':'Password is wrong','success':'404 NOT FOUND'})
                else:
                    payload = {
                            'profileID': user.profileID,
                            'email': user.email,
                            'exp': datetime.utcnow() + timedelta(seconds=20)
                        }
                    # accessToken = self.generateAccessToken(payload)
                    # print(accessToken)
                    message = 'Successfully login this user'
                    response = self.user_schema.jsonify(user)
                    response.payload= payload
                    response.message = message
                    response.status = '200 OK'
                    return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})

    def register(self,name,email,password,Age,Gender,MaritalStatus,Occupation):
        error = self.validateUser(email,password,status='register')
        if error is 'None':
            password = self.encryptPassword(password)
            user = User(name, email, password, Age,Gender,MaritalStatus,Occupation)
            self.dbSession.add(user)
            self.dbSession.commit()
            message = 'Successfully registered user'
            response = self.user_schema.jsonify(user)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})
    
    def deleteUser(self,id): 
        user = self.dbSession.query(User).get(id)
        if user :
            self.dbSession.delete(user)
            self.dbSession.commit()
            message = 'Successfully deleted this user'
            response = self.user_schema.jsonify(user)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no user for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
    
    def editUser(self,id,name,email,password,Age,Gender,MaritalStatus,Occupation):
        error = self.validateUser(email,password,status='edit')
        password = self.encryptPassword(password)
        if error is 'None':
            user = self.dbSession.query(User).get(id) 
            if user is None:
                return  jsonify({'message':'There is no user this id','success':'404 NOT FOUND'})
            else:
                user.name = name
                user.email = email
                user.password = password
                user.Age = Age
                user.Gender = Gender
                user.MaritalStatus = MaritalStatus
                user.Occupation = Occupation
                self.dbSession.commit()

                message = 'Successfully added this user'
                response = self.user_schema.jsonify(user)
                response.message = message
                response.status = '200 OK'
                return response

    def validateUser(self,email,password,status):
        error = 'None'
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])"
        if not email:
            error = 'Email is required.'
        elif not re.fullmatch(regex, email):
            error = 'Email is not valid.'
        elif not password:
            error = 'Password is required.'
        elif len(password) <6:
            error = 'Password length must be 6.'
        elif not re.match(password_pattern, password):
            error = 'Password must be one uppercase and lowercase and one digit character and one special character'
        result = self.dbSession.query(User).filter_by(email=email).first()
        if status == 'register':
            if result is not None:
                error = 'User is already exist.'
        return error
    
    # def logout(self,id):
    #     return id
    