def cleaningRecipe(recipe_list):
    recipe_list['Directions'] = recipe_list['Directions'].fillna('No Description')  #Direction column doesnt necessary to has a value or not.
                                                                                    # So I filled with 'No Description'
    recipe_list['RecommendIngredients'] = recipe_list['Ingredients'].map(lambda x:x.replace(' ',"")) #delete ' ' blank for each Ingredients like white suger wihtesugar
    recipe_list['RecommendIngredients'] = recipe_list['RecommendIngredients'].str.split(',') #convert ingredients column values to array 
    return recipe_list   