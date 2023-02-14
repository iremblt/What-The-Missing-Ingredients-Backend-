import numpy as np

class embeddingVectorizer(object):
    def __init__(self, model_cbow):
        self.model_cbow = model_cbow
        self.vector_size = model_cbow.wv.vector_size

    def fit(self):  
        return self

    def transform(self, items): 
        vector = self.average_list(items)
        return vector

    def average(self, item):
        mean = []
        for word in item:
            # if word in self.model_cbow.wv.index_to_key:
            if word in self.model_cbow.wv.index_to_key:
                mean.append(self.model_cbow.wv.get_vector(word))

        if not mean: 
            return np.zeros(self.vector_size)
        else:
            mean = np.array(mean).mean(axis=0)
            return mean

    def average_list(self, items):
        return np.vstack([self.average(item) for item in items])
