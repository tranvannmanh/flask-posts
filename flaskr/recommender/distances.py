import numpy as np
from scipy.stats import entropy

def jensen_shannon(doc_distribute, matrix_distribute):
    """
    This function implements a Jensen-Shannon similarity
    between the input query (an LDA topic distribution for a document)
    and the entire corpus of topic distributions.
    It returns an array of length M (the number of documents in the corpus)
    """
    p = doc_distribute[None, :].T
    q = matrix_distribute.T
    m = .5 * (p + q)
    return np.sqrt(.5 * (entropy(q, m) + entropy(p, m)))

def get_most_similar_news(doc_distribute, matrix_distribute, k=10):
    """
    This function implements the Jensen-Shannon distance above
    and returns the top k indices of the smallest jensen shannon distances
    """
    # List of jensen-shannon distances
    sims = jensen_shannon(doc_distribute=doc_distribute, matrix_distribute=matrix_distribute)

    # return index of most K similar distribution from list
    return np.argsort(sims)[:k]