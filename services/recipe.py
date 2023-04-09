from entities.recipe import Recipe
from models.recipe import RecipeSchema
from models.recipe import RecipeSchemaWithAvgRating
from flask import jsonify
import json
from entities.databaseSessionManager import SessionManager


import nltk
import string
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from services.vectorizerIngredients import embeddingVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from services.review import ReviewCRUD
from entities.review import Review

nltk.download('stopwords')
nltk.download('wordnet')

class RecipeCRUD():
    dbSession = SessionManager().session
    recipe_schemas = RecipeSchema(many=True)
    recipe_schema = RecipeSchema()
    recipe_schema_avg_rating = RecipeSchemaWithAvgRating()
    recipe_schema_avg_ratings = RecipeSchemaWithAvgRating(many=True)
    review_services = ReviewCRUD()

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
    
    def getRecipeListWithPagination(self,Page_Size,Page_Number_Per_Page):
        recipe_list = self.dbSession.query(Recipe).all()
        if len(recipe_list) == 0 :
            message = 'There is no recipe yet. You can add a new recipe'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            message = 'Successfully listed all recipes'
            offset = Page_Number_Per_Page * (Page_Size - 1)
            recipe_list_pagination =self.dbSession.query(Recipe).order_by(Recipe.RecipeID.desc()).offset(offset).limit(Page_Number_Per_Page).all()
            results = self.recipe_schemas.dump(recipe_list_pagination)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
        
    def getRecipeListWithPaginationOrderByReviewCount(self,Page_Size,Page_Number_Per_Page):
        recipe_list = self.dbSession.query(Recipe).all()
        if len(recipe_list) == 0 :
            message = 'There is no recipe yet. You can add a new recipe'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            message = 'Successfully listed all recipes'
            offset = Page_Number_Per_Page * (Page_Size - 1)
            recipe_list_pagination =self.dbSession.query(Recipe).order_by(Recipe.Review_Count.desc()).offset(offset).limit(Page_Number_Per_Page).all()
            results = self.recipe_schemas.dump(recipe_list_pagination)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
        
    def getRecipeListByAvgRating(self,idList):
        count = 0
        avg_rate = 0
        recipe_list = []
        if len(idList):
            for id in idList:
                recipe = self.dbSession.query(Recipe).get(id)
                if recipe :
                    count = 0
                    avg_rate = 0
                    reviews_list = self.dbSession.query(Review).filter_by(RecipeID=recipe.RecipeID).all()
                    for review in reviews_list:
                        count = count + review.Rate
                    if len(reviews_list):
                        avg_rate = count / len(reviews_list)
                    recipe.RatingAvg = round(avg_rate,1)
                    recipe_list.append(recipe)
            message = 'Successfully detailed this recipe'
            results = self.recipe_schema_avg_ratings.dump(recipe_list)
            response = jsonify(results)
            return response 
        else:
            recipe = self.dbSession.query(Recipe).get(id)
            if recipe :
                reviews_list = self.dbSession.query(Review).filter_by(RecipeID=recipe.RecipeID).all()
                for review in reviews_list:
                    count = count + review.Rate
                if len(reviews_list):
                    avg_rate = count / len(reviews_list)
                recipe.RatingAvg = round(avg_rate,1)
                message = 'Successfully detailed this recipe'
                results = self.recipe_schema_avg_rating.dump(recipe)
                response = jsonify(results)
                return response 
            else:
                message = 'There is no recipe for this id'
                return jsonify({'message':message,'success':'404 NOT FOUND'})
    
    def searchByRecipeName(self,Recipe_Name,Page_Size,Page_Number_Per_Page):
        recipe_list = self.dbSession.query(Recipe).all()
        if len(recipe_list) == 0 :
            message = 'There is no recipe yet. You can add a new recipe'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            message = 'Successfully listed all recipes'
            recipe_list_search =self.dbSession.query(Recipe).filter(Recipe.Recipe_Name.contains(Recipe_Name)).all()
            if len(recipe_list_search) == 0 :
                message = 'There is no recipe name in your search query.'
                return jsonify({'message':message,'success':'404 NOT FOUND'})
            else:
                offset = Page_Number_Per_Page * (Page_Size - 1)
                recipe_list_pagination = self.dbSession.query(Recipe).filter(Recipe.Recipe_Name.contains(Recipe_Name)).order_by(Recipe.RecipeID.desc()).offset(offset).limit(Page_Number_Per_Page).all()
                results = self.recipe_schemas.dump(recipe_list_pagination)
                # results = self.recipe_schemas.dump(recipe_list_search)
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
        error = self.validateRecipe('create',Recipe_Name, Recipe_Photo,Total_Time,Ingredients,Directions)
        if error is 'None':
            recipe = Recipe(Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions)
            self.dbSession.add(recipe)
            self.dbSession.commit()
            message = 'Successfully added this recipe'
            response = self.recipe_schema.jsonify(recipe)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})
    
    def recommendRecipe(self,ingredients):
        rec = self.preaperRecommendation(ingredients)
        json_data = rec.to_json(orient="records")
        json_load = json.loads(json_data)
        response = json.dumps(json_load)
        return response    
    
    def mostCommonIngredients(self):
        vocabulary = nltk.FreqDist()
        most_common_20_words = []
        recipe_list = self.dbSession.query(Recipe).all()
        for recipe in recipe_list:
            ingredients = recipe.Ingredients.split(',')
            # ingredients = recipe.Ingredients.replace(' ',"").split(',')
            vocabulary.update(ingredients)
        for word, frequency in vocabulary.most_common(20):
            most_common_20_words.append(word)
            print(f'{word} ; {frequency}')
        return most_common_20_words
    
    def convertList(string):
        return list(string.split(" "))

    def ingredientPrepocessing(self):
        # commonIngredients = self.mostCommonIngredients()
        recipe_list = self.dbSession.query(Recipe).all()
        ingredient_list = []
        for recipe in recipe_list:
            ingredient_list.append(recipe.Ingredients.split(','))
            # ingredient_list.append(recipe.Ingredients.replace(' ',"").split(','))
        if isinstance(ingredient_list, list):
            ingredient_list = ingredient_list
        else:
            ingredient_list = self.convertList(ingredient_list)
        translator = str.maketrans('', '', string.punctuation)
        lemmatizer = WordNetLemmatizer()
        parsed_ingredient = []
        parsed_ingredient_list = []
        for ingredients in ingredient_list:
            for ingredient in ingredients:
                ingredient.translate(translator)
                items = re.split(' |-', ingredient)
                items = [word for word in items if word.isalpha()]
                items = [word.lower() for word in items]
                items = [lemmatizer.lemmatize(word) for word in items]
                stop_words = set(stopwords.words('english'))
                items = [word for word in items if word not in stop_words]
                # items = [word for word in items if word not in commonIngredients]
                if items:
                    parsed_ingredient.append(' '.join(items))
            if len(parsed_ingredient):
                parsed_ingredient_list.append(parsed_ingredient)
                parsed_ingredient = []
            else:
                parsed_ingredient_list.append([])
        return parsed_ingredient_list

    def inputIngredientPrepocessing(self,input_ingredients):
            # commonIngredients = self.mostCommonIngredients()
            ingredient_list = []
            for input in input_ingredients:
                ingredient_list.append(input)
                # ingredient_list.append(input.replace(' ',""))
            if isinstance(input_ingredients, list):
                input_ingredients = input_ingredients
            else:
                input_ingredients = self.convertList(input_ingredients)
            translator = str.maketrans('', '', string.punctuation)
            lemmatizer = WordNetLemmatizer()
            parsed_ingredient = []
            for ingredient in input_ingredients:
                ingredient.translate(translator)
                items = re.split(' |-', ingredient)
                items = [word for word in items if word.isalpha()]
                items = [word.lower() for word in items]
                items = [lemmatizer.lemmatize(word) for word in items]
                stop_words = set(stopwords.words('english'))
                items = [word for word in items if word not in stop_words]
                # items = [word for word in items if word not in commonIngredients]
                if items:
                    parsed_ingredient.append(' '.join(items))
            return parsed_ingredient   


    def corpus_sorted(self,parsed_data):
        corpus_sorted = []
        for i in parsed_data:
            i.sort()
            corpus_sorted.append(i)
        return corpus_sorted

    def get_window(self,corpus):
        lengths = [len(doc) for doc in corpus]
        avg_len = float(sum(lengths)) / len(lengths)
        return round(avg_len)

    def getModelAndParsed(self,corpus):
        model_word2 = Word2Vec(corpus, sg=0, workers=8, window = self.get_window(corpus), min_count=1, vector_size=100)
        model_word2.save('models/model_word2.bin')

    def recommendRecipes(self,scores,N):
        recipe_list = self.dbSession.query(Recipe).all()
        sorted_top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:N]
        recommendation = pd.DataFrame(columns=["Recipe_Name", "Ingredients","Author","Cook_Time","Prepare_Time","Recipe_Photo","Total_Time","RecipeID"])
        count = 0
        for i in sorted_top:
            for index, recipe in enumerate(recipe_list):
                if(index == i):
                    recommendation.at[count, "Recipe_Name"] = recipe.Recipe_Name
                    recommendation.at[count, "Ingredients"] = recipe.Ingredients
                    recommendation.at[count, "Author"] = recipe.Author
                    recommendation.at[count, "Cook_Time"] = recipe.Cook_Time
                    recommendation.at[count, "Prepare_Time"] = recipe.Prepare_Time
                    recommendation.at[count, "Recipe_Photo"] = recipe.Recipe_Photo
                    recommendation.at[count, "Total_Time"] = recipe.Total_Time
                    recommendation.at[count, "RecipeID"] = recipe.RecipeID
                    recommendation.at[count, "score"] = f"{scores[i]}"
                    count += 1
        return recommendation
    
    def preaperRecommendation(self,ingredients):
            input = self.inputIngredientPrepocessing(ingredients.split(","))
            parsed_data = self.ingredientPrepocessing()
            corpus = self.corpus_sorted(parsed_data)
            self.getModelAndParsed(corpus)
            model = Word2Vec.load("models/model_word2.bin")
            model.init_sims(replace=True)
            if model:
                print("Successfully loaded model")
            vector = embeddingVectorizer(model)
            item_vec = vector.transform(corpus)
            item_vec = [doc.reshape(1, -1) for doc in item_vec] 
            assert len(item_vec) == len(corpus)
            input_embedding = vector.transform([input])[0].reshape(1, -1)
            cos_sim = map(lambda x: cosine_similarity(input_embedding, x)[0][0], item_vec)
            scores = list(cos_sim)
            recommendations = self.recommendRecipes(scores,N=20)
            return recommendations

    def deleteRecipe(self,id):
        recipe = self.dbSession.query(Recipe).get(id)
        if recipe :
            self.dbSession.delete(recipe)
            self.dbSession.commit()
            message = 'Successfully deleted this recipe'
            response = self.recipe_schema.jsonify(recipe)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no recipe for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def editRecipe(self,id,Recipe_Name, Review_Count, Recipe_Photo, Author, Prepare_Time, Cook_Time,Total_Time,Ingredients,Directions):
        error = self.validateRecipe('edit',Recipe_Name, Recipe_Photo,Total_Time,Ingredients,Directions)
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

                message = 'Successfully added this recipe'
                response = self.recipe_schema.jsonify(recipe)
                response.message = message
                response.status = '200 OK'
                return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})

    def validateRecipe(self,status,Recipe_Name, Recipe_Photo, Total_Time,Ingredients,Directions):
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
        if status == 'create':
            if result is not None:
                error = 'Recipe is already exist.'
        return error