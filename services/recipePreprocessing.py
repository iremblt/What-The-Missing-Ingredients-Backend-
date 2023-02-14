import nltk
import string
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('wordnet')

def mostCommonWords(ingredients):
    vocabulary = nltk.FreqDist()
    most_common_20_words = []
    for ingredient in ingredients:
        vocabulary.update(ingredient)
    for word, frequency in vocabulary.most_common(20):
        most_common_20_words.append(word)
        print(f'{word} ; {frequency}')
    return most_common_20_words

def convertList(string):
    return list(string.split(" "))

def ingredientPrepocessing(ingredients,commonIngredients): #delete common words and different variantions of the words
    measures = ['inch', 't', 'T','once']
    words_to_remove = commonIngredients
    if isinstance(ingredients, list):
        ingredients = ingredients
    else:
        ingredients = convertList(ingredients)
    
    #Get rid of all the punctuation
    translator = str.maketrans('', '', string.punctuation)

    # initialize nltk's lemmatizer    
    lemmatizer = WordNetLemmatizer()
    ingredient_list = []
    for i in ingredients:

        i.translate(translator)

        # hyphens split spaces
        items = re.split(' |-', i)

        # Get rid of non alphabet words
        items = [word for word in items if word.isalpha()]

        # Turn lowercase
        items = [word.lower() for word in items]

        # Lemmatize words
        items = [lemmatizer.lemmatize(word) for word in items]

        # Get rid of stop words
        stop_words = set(stopwords.words('english'))
        items = [word for word in items if word not in stop_words]

        # Get rid of common and measures
        items = [word for word in items if word not in measures]
        items = [word for word in items if word not in words_to_remove]

        if items:
            ingredient_list.append(' '.join(items))
    return ingredient_list