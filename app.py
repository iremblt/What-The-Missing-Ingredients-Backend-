import flask
from flask import request
from services.recipe import RecipeCRUD
from services.review import ReviewCRUD
from services.user import UserCRUD

app = flask.Flask(__name__)

recipeServices = RecipeCRUD()
reviewServices = ReviewCRUD()
userServices = UserCRUD()


@app.route('/', methods=(['GET']))
def home():
    return 'Hello'

@app.route('/Recipe/List', methods=(['GET']))
def recipeList():
    args = request.args
    try:
        if(getattr(request, 'json', None)):
                Recipe_Name = request.json['RecipeName']
                Page_Size = request.json['PageSize']
                Page_Number_Per_Page = request.json['PageNumberPerPage']
                recipe_list = recipeServices.searchByRecipeName(Recipe_Name,Page_Size,Page_Number_Per_Page)
                return recipe_list
    except:
        try:
            if(getattr(request, 'json', None)):
                Recipe_Name = request.json['RecipeName']
                recipe_list = recipeServices.searchByRecipeName(Recipe_Name,1,20)
                return recipe_list
        except:
            try:
                if(getattr(request, 'json', None)):
                    Page_Size = request.json['PageSize']
                    Page_Number_Per_Page = request.json['PageNumberPerPage']
                    recipe_list = recipeServices.getRecipeListWithPagination(Page_Size,Page_Number_Per_Page)
                    return recipe_list
            except:
                try:
                    if(len(args)):
                        if(getattr(request, 'args', None)):
                                print(request.args)
                                Recipe_Name = args.get('RecipeName')
                                Page_Size = int(args.get('PageSize'))
                                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                                recipe_list = recipeServices.searchByRecipeName(Recipe_Name,Page_Size,Page_Number_Per_Page)
                                return recipe_list
                    else:
                        recipe_list = recipeServices.getRecipeList()
                        return recipe_list
                except:
                    try:
                        if(getattr(request, 'args', None)):
                            Recipe_Name = args.get('RecipeName')
                            recipe_list = recipeServices.searchByRecipeName(Recipe_Name,0,0)
                            return recipe_list
                    except:
                        try:
                            if(getattr(request, 'args', None)):
                                Page_Size = int(args.get('PageSize'))
                                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                                recipe_list = recipeServices.getRecipeListWithPagination(Page_Size,Page_Number_Per_Page)
                                return recipe_list
                        except:
                            recipe_list = recipeServices.getRecipeList()
                            return recipe_list

@app.route('/Recipe/Most/Rating', methods=(['GET']))
def mostPopularRecipes():
    args = request.args
    try:
        if(getattr(request, 'json', None)):
            Page_Size = request.json['PageSize']
            Page_Number_Per_Page = request.json['PageNumberPerPage']
            recipe_list = recipeServices.getRecipeListWithPaginationOrderByReviewCount(Page_Size,Page_Number_Per_Page)
            return recipe_list
    except:
        if(len(args)):
                if(getattr(request, 'args', None)):
                    Page_Size = int(args.get('PageSize'))
                    Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                    recipe_list = recipeServices.getRecipeListWithPaginationOrderByReviewCount(Page_Size,Page_Number_Per_Page)
                    return recipe_list
                else:
                    recipe_list = recipeServices.getRecipeList()
                    return recipe_list

@app.route('/Recipe/Details/<id>', methods=(['GET']))
def recipeDetail(id):
    return recipeServices.getRecipeById(id)

@app.route('/Recipe/Recommendation', methods=(['POST']))
def recommendation():
    ingredients = request.json['ingredients']
    return recipeServices.recommendRecipe(ingredients)

@app.route('/Recipe/Upload/Recipe/Image', methods=(['POST']))
def upload():
    Recipe_Photo = request.files['Recipe_Photo']
    return recipeServices.uploadRecipeImage(Recipe_Photo)

@app.route('/Recipe/Add', methods=(['POST']))
def add():
    Recipe_Name = request.json['RecipeName']
    Review_Count = request.json['ReviewCount']
    Recipe_Photo = request.json['RecipePhoto']
    Author = request.json['Author']
    Prepare_Time = request.json['PrepareTime']
    Cook_Time= request.json['CookTime']
    Total_Time= request.json['TotalTime']
    Ingredients= request.json['Ingredients']
    Directions= request.json['Directions']
    return recipeServices.addRecipe(Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions)
    
@app.route('/Recipe/Edit/<id>', methods=(['PUT']))
def edit(id):
    Recipe_Name = request.json['RecipeName']
    Review_Count = request.json['ReviewCount']
    Recipe_Photo = request.json['RecipePhoto']
    Author = request.json['Author']
    Prepare_Time = request.json['PrepareTime']
    Cook_Time= request.json['CookTime']
    Total_Time= request.json['TotalTime']
    Ingredients= request.json['Ingredients']
    Directions= request.json['Directions']
    return recipeServices.editRecipe(id,Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions)

@app.route('/Recipe/Edit/ReviewCount/<id>', methods=(['PUT']))
def reviewCountRecipe(id):
    count = request.json['count']
    return recipeServices.recipeReviewCountEdit(id,count)

@app.route('/Recipe/delete/<id>', methods=(['DELETE']))
def deleteRecipe(id):
    return recipeServices.deleteRecipe(id)

@app.route('/Review/List', methods=(['GET']))
def reviewList():
    review_list = reviewServices.getReviewList()
    return review_list

@app.route('/Recipe/Review/Details/<id>', methods=(['GET']))
def recipeReviews(id):
    args = request.args
    try:
        if(getattr(request, 'json', None)):
                Page_Size = request.json['PageSize']
                Page_Number_Per_Page = request.json['PageNumberPerPage']
                review_list = reviewServices.getReviewsByPaginationRecipeID(id,Page_Size,Page_Number_Per_Page)
                return review_list
    except:
                try:
                    if(len(args)):
                        if(getattr(request, 'args', None)):
                                Page_Size = int(args.get('PageSize'))
                                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                                review_list = reviewServices.getReviewsByPaginationRecipeID(id,Page_Size,Page_Number_Per_Page)
                                return review_list
                    else:
                        review_list = reviewServices.getReviewsByRecipeID(id)
                        return review_list
                except:
                        try:
                            if(getattr(request, 'args', None)):
                                Page_Size = int(args.get('PageSize'))
                                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                                review_list = reviewServices.getReviewsByPaginationRecipeID(id,Page_Size,Page_Number_Per_Page)
                                return review_list
                        except:
                            review_list = reviewServices.getReviewsByRecipeID(id)
                            return review_list

@app.route('/Recipe/Avarage/Rate', methods=(['GET']))
def avgRatingWithRecipes():
    args = request.args
    try:
        if(getattr(request, 'json', None)):
            ids = request.json['ids']
            recipe_list =  recipeServices.getRecipeListByAvgRating(ids)
            return recipe_list
    except:
        if(len(args)):
            if(getattr(request, 'args', None)):
                ids = []
                ids.append(args.get('0'))
                ids.append(args.get('1'))
                recipe_list = recipeServices.getRecipeListByAvgRating(ids)
                return recipe_list

@app.route('/User/Review/Details/<id>', methods=(['GET']))
def userReviews(id):
    args = request.args
    try:
        if(getattr(request, 'json', None)):
            Page_Size = request.json['PageSize']
            Page_Number_Per_Page = request.json['PageNumberPerPage']
            review_list = reviewServices.getReviewsByProfileID(id,Page_Size,Page_Number_Per_Page)
            return review_list
    except:
        try:
            if(getattr(request, 'args', None)):
                Page_Size = int(args.get('PageSize'))
                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                review_list = reviewServices.getReviewsByProfileID(id,Page_Size,Page_Number_Per_Page)
                return review_list
        except:
            review_list = reviewServices.getReviewsByProfileID(id,1,1000)
            return review_list

@app.route('/Review/Add', methods=(['POST']))
def addReview():
    RecipeID = request.json['RecipeID']
    profileID = request.json['profileID']
    Rate = request.json['Rate']
    Comments = request.json['Comments']
    return reviewServices.addReview(RecipeID, profileID, Rate, Comments)
    
@app.route('/Review/Edit/<id>', methods=(['PUT']))
def editReview(id):
    RecipeID = request.json['RecipeID']
    profileID = request.json['profileID']
    Rate = request.json['Rate']
    Comments = request.json['Comments']
    return reviewServices.editReview(id,RecipeID, profileID, Rate, Comments)

@app.route('/Review/delete/<id>', methods=(['DELETE']))
def deleteReview(id):
    return reviewServices.deleteReview(id)

@app.route('/User/List', methods=(['GET']))
def userList():
    user_list = userServices.getUserList()
    return user_list

@app.route('/Chef/List', methods=(['GET']))
def chefList():
    args = request.args
    try:
        if(getattr(request, 'json', None)):
                name = request.json['name']
                chef_list = userServices.searchByChefName(name)
                return chef_list
    except:
            try:
                if(getattr(request, 'json', None)):
                    Page_Size = request.json['PageSize']
                    Page_Number_Per_Page = request.json['PageNumberPerPage']
                    chef_list = userServices.getChefListWithPagination(Page_Size,Page_Number_Per_Page)
                    return chef_list
            except:
                try:
                    if(len(args)):
                        if(getattr(request, 'args', None)):
                                name = args.get('name')
                                chef_list = userServices.searchByChefName(name)
                                return chef_list
                    else:
                        chef_list = userServices.getAllChefList()
                        return chef_list
                except:
                        try:
                            if(getattr(request, 'args', None)):
                                Page_Size = int(args.get('PageSize'))
                                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                                chef_list = userServices.getChefListWithPagination(Page_Size,Page_Number_Per_Page)
                                return chef_list
                        except:
                            chef_list = userServices.getAllChefList()
                            return chef_list

@app.route('/User/Detail/<id>', methods=(['GET']))
def user_details(id):
    return userServices.getUserByID(id)

@app.route('/User/Recipe/Detail/<id>', methods=(['GET']))
def user_recipes(id):
    args = request.args
    try:
        if(getattr(request, 'json', None)):
            Page_Size = request.json['PageSize']
            Page_Number_Per_Page = request.json['PageNumberPerPage']
            recipe_list = userServices.getUserByIDRecipes(id,Page_Size,Page_Number_Per_Page)
            return recipe_list
    except:
        try:
            if(getattr(request, 'args', None)):
                Page_Size = int(args.get('PageSize'))
                Page_Number_Per_Page = int(args.get('PageNumberPerPage'))
                recipe_list = userServices.getUserByIDRecipes(id,Page_Size,Page_Number_Per_Page)
                return recipe_list
        except:
            recipe_list = userServices.getUserByIDRecipes(id,1,1000)
            return recipe_list

@app.route('/Login', methods=(['POST']))
def login():
    email = request.json['email']
    password = request.json['password']
    return userServices.login(email,password)

@app.route('/Register', methods=(['POST']))
def register():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    Age = request.json['Age']
    Gender = request.json['Gender']
    MaritalStatus = request.json['MaritalStatus']
    Occupation = request.json['Occupation']
    return userServices.register(name,email,password,Age,Gender,MaritalStatus,Occupation)
    
@app.route('/User/Edit/<id>', methods=(['PUT']))
def editUser(id):
    name = request.json['name']
    email = request.json['email']
    Age = request.json['Age']
    Gender = request.json['Gender']
    MaritalStatus = request.json['MaritalStatus']
    Occupation = request.json['Occupation']
    return userServices.editUser(id,name,email,Age,Gender,MaritalStatus,Occupation)

@app.route('/User/delete/<id>', methods=(['DELETE']))
def deleteUser(id):
    return userServices.deleteUser(id)

@app.route('/User/Change/Password/<id>', methods=(['PUT']))
def changePassword(id):
    newPassword = request.json['newPassword']
    currentPassword = request.json['currentPassword']
    currentWritedPassword = request.json['currentWritedPassword']
    user = userServices.changePassword(id,newPassword,currentPassword,currentWritedPassword)
    return user


if __name__ == '__main__':
    app.run()

app.run(debug=True)