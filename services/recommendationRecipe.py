import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from services.cleaningRecipe import cleaningRecipe
from services.recipePreprocessing import mostCommonWords,ingredientPrepocessing
from services.getCorpusWord2Vec import getModel,corpus_sorted
from services.vectorizerIngredients import embeddingVectorizer

def recommendRecipes(scores,recipeList):
    
    # order the scores and get the highest scores
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

    # create dataframe for recommendation
    recommendation = pd.DataFrame(columns=["recipe", "ingredients", "score", "image"])
    count = 0
    for i in top:
        recommendation.at[count, "recipe"] = recipeList['Recipe Name'][i]
        recommendation.at[count, "ingredients"] = recipeList['Ingredients'][i]
        recommendation.at[count, "image"] = recipeList["Recipe Photo"][i]
        recommendation.at[count, "id"] = recipeList["RecipeID"][i]
        recommendation.at[count, "author"] = recipeList["Author"][i]
        recommendation.at[count, "score"] = f"{scores[i]}"
        count += 1
    return recommendation

def preaperRecommendation(ingredients):

    recipe_list = pd.read_csv('clean_recipes.csv', delimiter=';')
    cleanedRecipeList = cleaningRecipe(recipe_list)
    commonIngredients = mostCommonWords(cleanedRecipeList['RecommendIngredients'])
    processed_ingredient_list= []
    for item in cleanedRecipeList['RecommendIngredients']:
        processed_ingredient_list.append(ingredientPrepocessing(item,commonIngredients))
    cleanedRecipeList['RecommendIngredients'] = processed_ingredient_list
    getModel(cleanedRecipeList)
    corpus = corpus_sorted(cleanedRecipeList['RecommendIngredients'])

    # load in word2vec model
    model = Word2Vec.load("models/model_cbow.bin")

    # normalize embeddings
    model.init_sims(replace=True)
    
    # get average embdeddings for each document
    vector = embeddingVectorizer(model)

    item_vec = vector.transform(corpus)
    item_vec = [item.reshape(1, -1) for item in item_vec]
    assert len(item_vec) == len(corpus)
    input = ingredients.split(",")
    input = ingredientPrepocessing(input,commonIngredients)

    # get embeddings for ingredient vector
    input_embedding = vector.transform([input])[0].reshape(1, -1)  

    # get cosine similarity between input embedding and all the document embeddings
    cos_sim = map(lambda x: cosine_similarity(input_embedding, x)[0][0], item_vec)
    recommendations = recommendRecipes(list(cos_sim),cleanedRecipeList)

    return recommendations
