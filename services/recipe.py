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
        results = self.recipe_schemas.dump(recipe_list)
        return jsonify(results)
    
    def getRecipeById(self,id):
        recipe = self.dbSession.query(Recipe).get(id)
        return self.recipe_schema.jsonify(recipe)

    def addRecipe(self,Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions):
        recipe = Recipe(Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions)
        self.dbSession.add(recipe)
        self.dbSession.commit()

        RecipeID = recipe.RecipeID
        recipeCSV = [Recipe_Name,Review_Count,Recipe_Photo,Author,Prepare_Time,Cook_Time,Total_Time,Ingredients,Directions,RecipeID] 

        with open(r'clean_recipes.csv', 'a',newline='') as f:
            writer_data = writer(f, delimiter = ";")
            writer_data.writerow(recipeCSV)
        
        return self.recipe_schema.jsonify(recipe)
    
    def recommendRecipe(self,ingredients):
        rec = preaperRecommendation(ingredients)
        json_data = rec.to_json(orient="records")
        json_load = json.loads(json_data)
        response = json.dumps(json_load)
        return response
    
    def deleteRecipe(self,id): #Tek tek her satıra bakıp eğer id 7001 diyelim reviewCount da 7001 ise onu da siler!!
        recipe = self.dbSession.query(Recipe).get(id)
        self.dbSession.delete(recipe)
        self.dbSession.commit()
        
        lines = list()
        with open('clean_recipes.csv', 'r') as readFile:
            read = reader(readFile,delimiter = ";")
            for row in read:
                if len(row)>0:
                    lines.append(row)
                for field in row:
                    if field == id:
                        lines.remove(row)
        with open('clean_recipes.csv', 'w') as writeFile:
            write = writer(writeFile,delimiter = ";")
            write.writerows(lines)

        return self.recipe_schema.jsonify(recipe)
    
    def editRecipe(self,id,Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions):
        recipe = self.dbSession.query(Recipe).get(id) 
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

        return self.recipe_schema.jsonify(recipe)