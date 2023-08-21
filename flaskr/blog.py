from flask import (
    Blueprint,
    request,
    Response,
    session,
)
from sqlalchemy.sql.expression import func
import numpy as np
from . import database
from . import models
import json
from . import dto
from . import config
from . import recommender

bp = Blueprint('news', __name__, url_prefix='/api/news')
Category = models.Category
Posts = models.Posts
Recommend = models.Recommend
db = database.db
res = dto.response.Response
utils=recommender.utils
distances=recommender.distances

def load_model():
    import gensim
    import joblib

    # load LDA model
    lda_model = gensim.models.LdaModel.load(
        config.PATH_LDA_MODEL
    )
    # load corpus
    corpus = gensim.corpora.MmCorpus(
        config.PATH_CORPUS
    )
    # load dictionary
    id2word = gensim.corpora.Dictionary.load(
        config.PATH_DICTIONARY
    )
    # load documents topic distribution matrix
    doc_topic_dist = joblib.load(
        config.PATH_TOPICS_DOCS_DIST
    )
    # doc_topic_dist = np.array([np.array(dist) for dist in doc_topic_dist])

    return lda_model, corpus, id2word, doc_topic_dist

lda_model, corpus, id2word, topics_docs_dist = load_model()

@bp.route('/get-similar', methods=['GET'])
def get_k_similar():
    items_size = request.args['itemsSize']
    news_id = request.args['newsId']
    news_base = Posts.query.filter_by(id=news_id).first()
    content_preprocessed = utils.simple_preprocessing(news_base.content)
    bow = id2word.doc2bow(content_preprocessed)
    topics_dist = np.array(
        [doc_top[1] for doc_top in lda_model.get_document_topics(bow=bow, minimum_probability=0.0)]
    )
    print(f'TYPES........ {type(topics_dist)} - {type(topics_docs_dist)}')
    
    # most_sims_offsets = [int(offset) for offset in distances.get_most_similar_news(topics_dist, np.array(topics_docs_dist), k=int(items_size))]
    most_sims_offsets = distances.get_most_similar_news(topics_dist, np.array(topics_docs_dist), k=int(items_size)+1)[1:]
    most_similar_news = []
    for offset in most_sims_offsets:
        news = Posts.query.offset(offset).first()
        most_similar_news.append({"id": news.id, "title": news.title})
    print('MOST_SIMILAR_OFFSET...... ', most_sims_offsets)
    return res(success=True, 
               result=most_similar_news,
               code=Response.status_code
               ).values()