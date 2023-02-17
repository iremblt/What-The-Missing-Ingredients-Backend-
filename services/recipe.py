from entities.recipe import Recipe
from models.recipe import RecipeSchema
from flask import jsonify
from csv import writer,reader
import json
from services.recommendationRecipe import preaperRecommendation
from entities.databaseSessionManager import SessionManager

class RecipeCRUD():
    dbSession = SessionManager().session
    recipe_schemas = RecipeSchema(many=True)
    recipe_schema = RecipeSchema()

    def getRecipeList(self):
        recipe_list = self.dbSession.query(Recipe).all()
        if len(recipe_list) == 0 :
            message = 'There is no recipe yet. You can add a new recipe'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            message = 'Successfully listed all recipes'
            results = self.recipe_schemas.dump(recipe_list)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
    
    def getRecipeById(self,id):
        recipe = self.dbSession.query(Recipe).get(id)
        if recipe :
            message = 'Successfully detailed this recipe'
            response = self.recipe_schema.jsonify(recipe)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no recipe for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def addRecipe(self,Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions):
        error = self.validateRecipe(Recipe_Name, Recipe_Photo,Total_Time,Ingredients,Directions)
        if error is 'None':
            recipe = Recipe(Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions)
            self.dbSession.add(recipe)
            self.dbSession.commit()

            RecipeID = recipe.RecipeID
            recipeCSV = [Recipe_Name,Review_Count,Recipe_Photo,Author,Prepare_Time,Cook_Time,Total_Time,Ingredients,Directions,RecipeID] 

            with open(r'clean_recipes.csv', 'a',newline='') as f:
                writer_data = writer(f, delimiter = ";")
                writer_data.writerow(recipeCSV)
            
            message = 'Successfully added this recipe'
            response = self.recipe_schema.jsonify(recipe)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})
    
    def recommendRecipe(self,ingredients):
        rec = preaperRecommendation(ingredients)
        json_data = rec.to_json(orient="records")
        json_load = json.loads(json_data)
        response = json.dumps(json_load)
        return response
    
    def deleteRecipe(self,id):
        recipe = self.dbSession.query(Recipe).get(id)
        if recipe :
            self.dbSession.delete(recipe)
            self.dbSession.commit()
            lines = list()
            with open('clean_recipes.csv', 'r') as readFile:
                read = reader(readFile,delimiter = ";")
                count = 0
                for row in read:
                    if len(row)>0:
                        lines.append(row)
                    for field in row:
                        count+=1
                        if(count %10 == 0):
                            if field == id:
                                lines.remove(row)
            with open('clean_recipes.csv', 'w') as writeFile:
                write = writer(writeFile,delimiter = ";")
                write.writerows(lines)
            message = 'Successfully deleted this recipe'
            response = self.recipe_schema.jsonify(recipe)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no recipe for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def editRecipe(self,id,Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions):
        error = self.validateRecipe(Recipe_Name, Recipe_Photo,Total_Time,Ingredients,Directions)
        if error is 'None':
            recipe = self.dbSession.query(Recipe).get(id) 
            if recipe is None:
                return  jsonify({'message':'There is no recipe this id','success':'404 NOT FOUND'})
            else:
                recipe.Recipe_Name = Recipe_Name
                recipe.Review_Count = Review_Count
                recipe.Recipe_Photo = Recipe_Photo
                recipe.Author = Author
                recipe.Prepare_Time = Prepare_Time
                recipe.Cook_Time = Cook_Time
                recipe.Total_Time = Total_Time
                recipe.Ingredients = Ingredients
                recipe.Directions = Directions
                self.dbSession.commit()

                lines = list()
                recipeCSV = [Recipe_Name,Review_Count,Recipe_Photo,Author,Prepare_Time,Cook_Time,Total_Time,Ingredients,Directions,id] 
                with open('clean_recipes.csv', 'r') as readFile:
                    read = reader(readFile,delimiter = ";")
                    for row in read:
                        if len(row)>0:
                            lines.append(row)
                        for field in row:
                            if field == id:
                                lines.remove(row)
                                lines.append(recipeCSV)
                
                with open('clean_recipes.csv', 'w') as writeFile:
                    write = writer(writeFile,delimiter = ";")
                    write.writerows(lines)

                message = 'Successfully added this recipe'
                response = self.recipe_schema.jsonify(recipe)
                response.message = message
                response.status = '200 OK'
                return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})

    def validateRecipe(self,Recipe_Name, Recipe_Photo, Total_Time,Ingredients,Directions):
        error = 'None'
        if not Recipe_Name:
            error = 'Recipe Name is required.'
        elif not Recipe_Photo:
            error = 'Recipe Photo is required.'
        elif not Total_Time:
            error = 'Total Time is required.'
        elif not Ingredients:
            error = 'Ingredients is required.'
        elif not Directions:
            error = 'Directions is required.'
        # Check if the Recipe Name is already exist
        result = self.dbSession.query(Recipe).filter_by(Recipe_Name=Recipe_Name).first()
        if result is not None:
            error = 'Recipe is already exist.'
        return error