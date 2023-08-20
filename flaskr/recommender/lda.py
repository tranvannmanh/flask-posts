from . import distances
from . import utils
from gensim.corpora import Dictionary
from gensim.models import LdaModel

PATH_DICTIONARY = "./flaskr/recommender/models/id2word.dictionary"
PATH_CORPUS = "./flaskr/recommender/models/corpus.mm"
PATH_LDA_MODEL = "./flaskr/recommender/models/LDA.model"
PATH_DOC_TOPIC_DIST = "./flaskr/recommender/models/doc_topic_dist.dat"

class LDAModel:
    def __init__(self, corpus, num_topics, passes, chunksize=100, update_every=1, alpha='auto', eta='auto',
                 per_word_topics=False):
        """
        :param sentences: list or iterable (recommend)
        """

        # data
        self.sentences = None

        # params
        self.lda_model = None
        self.dictionary = None
        self.corpus_bow = None
        self.corpus = corpus

        # hyperparams
        self.num_topics = num_topics
        self.alpha = alpha
        self.eta = eta
        self.passes = passes
        self.chunksize = chunksize
        # self.random_state = random_state
        self.update_every = update_every
        self.per_word_topics = per_word_topics

    def preprocessing_docs(self, sentences):
        return utils.simple_preprocessing(sentences)

    def _make_dictionary(self):
        preprocessed_docs = [self.preprocessing_docs(doc) for doc in self.corpus]
        self.dictionary = Dictionary(preprocessed_docs)
    
    def _doc2bow(self, doc):
        return self.dictionary.doc2bow(doc)
    
    def fit(self):
        from itertools import tee
        self._make_dictionary()
        self.corpus_bow=[self._doc2bow(doc) for doc in self.corpus]
        self.lda_model=LdaModel(
            corpus=self.corpus_bow, 
            id2word=self.dictionary,
            num_topics=self.num_topics, 
            alpha=self.alpha,
            eta=self.eta, 
            chunksize=self.chunksize
        )
        self.lda_model.save(PATH_LDA_MODEL)
        return self.lda_model

    def top_similar(self, doc_distribute, docs_topic_distribute, k_similar=10):
        return distances.get_most_similar_news(
            doc_distribute=doc_distribute, 
            matrix_distribute=docs_topic_distribute, 
            k=k_similar
        )
    