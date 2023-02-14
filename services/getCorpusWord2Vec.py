from gensim.models import Word2Vec

def corpus_sorted(item):
    corpus_sorted = []
    for i in item:
        i.sort()
        corpus_sorted.append(i)
    return corpus_sorted

# calculate average length of each item 
def get_window(corpus):
    lengths = [len(item) for item in corpus]
    avg_len = float(sum(lengths)) / len(lengths)
    return round(avg_len)

def getModel(recipe_list):
    corpus = corpus_sorted(recipe_list['RecommendIngredients'])

    # save CBOW Word2Vec model
    model_cbow = Word2Vec(corpus, sg=0, workers=8, window = get_window(corpus), min_count=1, vector_size=100)
    model_cbow.save('models/model_cbow.bin')
