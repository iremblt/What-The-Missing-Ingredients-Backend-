from entities.user import User
from models.user import UserSchema
from models.user import UserDetailSchema
from flask import jsonify
import re
from datetime import datetime, timedelta
import bcrypt
from Crypto.Random import get_random_bytes
from entities.databaseSessionManager import SessionManager
from entities.recipe import Recipe
from entities.review import Review
from models.recipe import RecipeSchema
from models.recipe import RecipeSchemaWithAvgRating
class UserCRUD():
    dbSession = SessionManager().session
    user_schemas = UserSchema(many=True)
    user_schema = UserSchema()
    user_detail_schema = UserDetailSchema()
    user_detail_schemas = UserDetailSchema(many=True)
    recipe_schemas = RecipeSchema(many=True)
    recipe_schema_avg_ratings = RecipeSchemaWithAvgRating(many=True)

    def getUserList(self):
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
        
    def getAllChefList(self):
        recipe_list = self.dbSession.query(Recipe)
        profileID_list = []
        user_list = []
        for recipe in recipe_list.all():
            if int(recipe.Author) not in profileID_list:
                profileID_list.append(int(recipe.Author))
                user_list.append(self.dbSession.query(User).get(int(recipe.Author)))
        results = self.user_schemas.dump(user_list)
        message = 'Successfully listed all chefs'
        response = jsonify(results)
        response.message = message
        response.status = '200 OK'
        return response
    
    def getChefListWithPagination(self,Page_Size,Page_Number_Per_Page):
        recipe_list = self.dbSession.query(Recipe).all()
        profileID_list = []
        user_list = []
        if len(recipe_list) == 0 :
            message = 'There is no chef yet. You can register then add your recipe.'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            offset = Page_Number_Per_Page * (Page_Size - 1)
            recipe_list_pagination =self.dbSession.query(Recipe).order_by(Recipe.RecipeID.desc()).offset(offset).limit(Page_Number_Per_Page).all()
            for recipe in recipe_list_pagination:
                if int(recipe.Author) not in profileID_list:
                    profileID_list.append(int(recipe.Author))
                    user_list.append(self.dbSession.query(User).get(int(recipe.Author)))
            for user in user_list:
                user_recipe_list = self.dbSession.query(Recipe).filter_by(Author= str(user.profileID)).all()
                user_review_list = self.dbSession.query(Review).filter_by(profileID= user.profileID).all()
                user.totalRecipes = len(user_recipe_list)
                user.totalReviews = len(user_review_list)
            results = self.user_detail_schemas.dump(user_list)
            message = 'Successfully listed all chefs'
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
        
    def searchByChefName(self,name):
        recipe_list = self.dbSession.query(Recipe).all()
        profileID_list = []
        user_list = []
        if len(recipe_list) == 0 :
            message = 'There is no recipe yet. You can add a new recipe'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            chef_list_search =self.dbSession.query(User).filter(User.name.contains(name)).all()
            if len(chef_list_search) == 0 :
                message = 'There is no chef name in your search query.'
                return jsonify({'message':message,'success':'404 NOT FOUND'})
            else:
                    recipe_list =self.dbSession.query(Recipe).order_by(Recipe.RecipeID.desc()).all()
                    for recipe in recipe_list:
                        if int(recipe.Author) not in profileID_list:
                            user = self.dbSession.query(User).get(int(recipe.Author))
                            if name.lower() in user.name.lower():
                                profileID_list.append(int(recipe.Author))
                                user_list.append(user)
                    results = self.user_schemas.dump(user_list)
                    message = 'Successfully listed all chefs'
                    response = jsonify(results)
                    response.message = message
                    response.status = '200 OK'
                    return response 
    
    def getUserByID(self,id):
        user = self.dbSession.query(User).get(id)
        if user :
            message = 'Successfully detailed this user'
            response = self.user_schema.dump(user)
            user_review_list = self.dbSession.query(Review).filter_by(profileID= user.profileID).all()
            user_recipe_list = self.dbSession.query(Recipe).filter_by(Author= str(user.profileID)).all()
            data = {
                "user" : response,
                "totalReviews" : len(user_review_list),
                "totalRecipes":len(user_recipe_list)
            }
            response = jsonify(data)
            return response
        else:
            message = 'There is no user for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
    
    def getUserByIDRecipes(self,id,Page_Size,Page_Number_Per_Page):
        user = self.dbSession.query(User).get(id)
        if user :
            offset = Page_Number_Per_Page * (Page_Size - 1)
            user_recipe_list =self.dbSession.query(Recipe).filter_by(Author= str(user.profileID)).order_by(Recipe.RecipeID.desc()).offset(offset).limit(Page_Number_Per_Page).all()
            results = self.recipe_schemas.dump(user_recipe_list)
            total_recipes = self.dbSession.query(Recipe).filter_by(Author= str(user.profileID)).all()
            count = 0
            avg_rate = 0
            recipe_list = []
            for recipe in user_recipe_list:
                count = 0
                avg_rate = 0
                reviews_list = self.dbSession.query(Review).filter_by(RecipeID=recipe.RecipeID).all()
                for review in reviews_list:
                    count = count + review.Rate
                if len(reviews_list):
                    avg_rate = count / len(reviews_list)
                recipe.RatingAvg = round(avg_rate,1)
                recipe_list.append(recipe)
            results = self.recipe_schema_avg_ratings.dump(recipe_list)
            data = {
                "total_recipes" : results,
                "total" : len(total_recipes),
            }
            response = jsonify(data)
            return response
    
    def encryptPassword(self,password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def decryptPassword(self,password,realpassword):
        return bcrypt.checkpw(password.encode('utf-8'), realpassword.encode('utf-8'))
    
    def login(self,email,password): 
        error = self.validateUser(email,password,status='login')
        if error is 'None':
            user = self.dbSession.query(User).filter_by(email=email).first()
            if user is None:
                jsonify({'message':'There is no user','success':'404 NOT FOUND'})
            else:
                if '@example.org' in user.email:
                    password = password
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
        
    def createForRecipe(self,name,email,password,Age,Gender,MaritalStatus,Occupation):
        password = self.encryptPassword(password)
        user = User(name, email, password, Age,Gender,MaritalStatus,Occupation)
        self.dbSession.add(user)
        self.dbSession.commit()
        return user
    
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
    
    def editUser(self,id,name,email,Age,Gender,MaritalStatus,Occupation):
        error = self.validateUser(email,'password',status='edit')
        if error is 'None':
            user = self.dbSession.query(User).get(id) 
            if user is None:
                return  jsonify({'message':'There is no user this id','success':'404 NOT FOUND'})
            else:
                user.name = name
                user.email = email
                user.password = user.password
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
    
    def changePassword(self,id,newPassword,currentPassword,currentWritedPassword):
        error = self.validatePassword(newPassword)
        if error is 'None':
            user = self.dbSession.query(User).get(id) 
            if user is None:
                return  jsonify({'message':'There is no user this id','success':'404 NOT FOUND'})
            password = self.decryptPassword(currentWritedPassword,currentPassword)
            if password is False:
                jsonify({'message':'Password is wrong','success':'404 NOT FOUND'})
            else:
                user.name = user.name
                user.email = user.email
                user.password = self.encryptPassword(newPassword)
                user.Age = user.Age
                user.MaritalStatus = user.MaritalStatus
                user.Gender = user.Gender
                user.Occupation = user.Occupation
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
            if status is not 'edit':
                error = 'Password is required.'
        elif len(password) <6:
            if status is not 'edit':
                error = 'Password length must be 6.'
        elif not re.match(password_pattern, password):
            if status is not 'edit':
                error = 'Password must be one uppercase and lowercase and one digit character and one special character'
        result = self.dbSession.query(User).filter_by(email=email).first()
        if status == 'register':
            if result is not None:
                error = 'User is already exist.'
        return error
    
    def validatePassword(self,password):
        error = 'None'
        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])"
        if not password:
            error = 'Password is required.'
        elif len(password) <6:
            error = 'Password length must be 6.'
        elif not re.match(password_pattern, password):
            error = 'Password must be one uppercase and lowercase and one digit character and one special character'
        return error