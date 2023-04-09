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
                                Recipe_Name = args.get('Recipe_Name')
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
                            Recipe_Name = args.get('Recipe_Name')
                            recipe_list = recipeServices.searchByRecipeName(Recipe_Name,1,20)
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

@app.route('/Recipe/delete/<id>', methods=(['DELETE']))
def deleteRecipe(id):
    return recipeServices.deleteRecipe(id)

@app.route('/Review/List', methods=(['GET']))
def reviewList():
    review_list = reviewServices.getReviewList()
    print(review_list)
    return review_list

@app.route('/Recipe/Review/Details/<id>', methods=(['GET']))
def recipeReviews(id):
    return reviewServices.getReviewsByRecipeID(id)

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
    return reviewServices.getReviewsByProfileID(id)

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
    chef_list = userServices.getChefList()
    return chef_list

@app.route('/User/Detail/<id>', methods=(['GET']))
def user_details(id):
    return userServices.getUserByID(id)

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
    password = request.json['password']
    Age = request.json['Age']
    Gender = request.json['Gender']
    MaritalStatus = request.json['MaritalStatus']
    Occupation = request.json['Occupation']
    return userServices.editUser(id,name,email,password,Age,Gender,MaritalStatus,Occupation)

@app.route('/User/delete/<id>', methods=(['DELETE']))
def deleteUser(id):
    return userServices.deleteUser(id)

# @app.route('/Logout', methods=(['POST']))
# def logout(id):
#     return userServices.logout(id)

# @app.route('/User/Reset/Password', methods=(['POST']))
# def logout(id):
#     return userServices.logout(id)


if __name__ == '__main__':
    app.run()

app.run(debug=True)