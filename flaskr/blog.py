from flask import (
    Blueprint,
    request,
    Response,
    session,
)
from sqlalchemy.sql.expression import func
from sqlalchemy import desc, asc, and_, or_
import numpy as np
from . import database
from . import models
import json
from . import dto
from . import config
from . import recommender
from datetime import datetime

bp = Blueprint('news', __name__, url_prefix='/api/news')
Category = models.Category
Posts = models.Posts
Recommend = models.Recommend
YouLike = models.YouLike
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


# Update list of news recommened by Collaborative-filtering method
def _collaborative_filtering_update_recommend(session_user_id, from_post_id):

    rec = YouLike.query.all()
    rec = [(re.user_id, re.post_id) for re in rec]
    # users_id = [re.user_id for re in rec]
    # print('USER LIKED... ', users_id)

    # get unique users list
    users_id = list(set([re[0] for re in rec]))
    # get unique news list
    posts_id = list(set([re[1] for re in rec]))
    
    rows_user_matrix = {}
    for user_id in users_id:
        rows_user_matrix[user_id] = []
        for post_id in posts_id:
            if (user_id, post_id) in rec:
                rows_user_matrix[user_id].append(1)
            else:
                rows_user_matrix[user_id].append(0)

    # create users like items matrix
    matrix_users_like_items = np.array([rows_user_matrix[user_id] for user_id in users_id])

    # Users Pearson correlation coefficients matrix
    pearson_matrix_corrcoef = np.corrcoef(matrix_users_like_items)[:, users_id.index(session_user_id)]

    # Get 3 most similar to session user
    user_id_similar_you_indexs = np.argsort(pearson_matrix_corrcoef)[:3]
    print('USER_ID_SIMILAR_INDEX... ', user_id_similar_you_indexs)
    post_update_list = []
    for index in user_id_similar_you_indexs:
        print('CHOOSEN SIMILAR USER... ', rows_user_matrix[users_id[index]])
        user_id_liked = rows_user_matrix[users_id[index]]
        for i in range(len(user_id_liked)):
            if rows_user_matrix[session_user_id] == 0 and user_id_liked[i] == 1:
                post_update_list.append(Recommend(user_id=session_user_id, post_id=posts_id[i], from_post_id=from_post_id))

    # update recommend list
    if post_update_list:
        db.session.add_all(post_update_list)
        db.session.commit()

    print('UPDATE RECOMMEND LIST ****************************************')


@bp.route('/get-by-type', methods=['GET'])
def get_new_by_type():
    type = request.args['type']
    page = request.args['page']
    size = request.args['pageSize']
    news = None
    if type:
        news = db.session.query(
            Posts
        ).filter(
            and_(
                Posts.type==type,
                Posts.content!=None
            )
        ).order_by(func.random()).paginate(page=int(page), per_page=int(size))
    else:
        news = Posts.query.filter(Posts.content != None)\
            .order_by(func.random())\
            .paginate(page=int(page), per_page=int(size))
    result = {
        "currentPage": int(page),
        "totalPage": 20,
        "pageItems": int(size),
        "data": [
            {
                "id": rec.id,
                "title": rec.title,
                "image": rec.image,
                "category": rec.type
            } for rec in news
        ]
    }
    return res(success=True, result=result).values()

@bp.route('/get-similar', methods=['GET'])
def get_k_similar():
    items_size = request.args['size']
    news_id = request.args['newsId']
    news_base = Posts.query.filter_by(id=news_id).first()
    content_preprocessed = utils.simple_preprocessing(news_base.content)
    bow = id2word.doc2bow(content_preprocessed)
    topics_dist = np.array(
        [doc_top[1] for doc_top in lda_model.get_document_topics(bow=bow, minimum_probability=0.0)]
    )
    # print(f'TYPES........ {type(topics_dist)} - {type(topics_docs_dist)}')
    
    # most_sims_offsets = [int(offset) for offset in distances.get_most_similar_news(topics_dist, np.array(topics_docs_dist), k=int(items_size))]
    most_sims_offsets = distances.get_most_similar_news(topics_dist, np.array(topics_docs_dist), k=int(items_size)+1)[1:]
    most_similar_news = []
    for offset in most_sims_offsets:
        news = Posts.query.offset(offset).first()
        most_similar_news.append({"id": news.id, 
                                  "title": news.title,
                                  "category": news.type
                                  })
    # print('MOST_SIMILAR_OFFSET...... ', most_sims_offsets)
    return res(success=True, 
               result=most_similar_news,
               code=Response.status_code
               ).values()

@bp.route('/you-like', methods=['POST'])
def update_you_like():
    user_id = session.get('user_id')
    news_id = request.args['newsId']
    _createAt = datetime.now()
    all_you_like = YouLike.query.filter_by(user_id=user_id).all()

    # remove old records
    if len(all_you_like) >= 8:
        old_records = YouLike.query.filter_by(user_id=user_id)\
                        .order_by(asc(YouLike.createAt))\
                        .limit(len(all_you_like) - 7)\
                        .all()
        
        for record in old_records:
            db.session.delete(record)
            db.session.commit()
            _update_recommend(user_id, postId=record.post_id, remove_old=True)
        # print('DELETE.................. ', deleted[0].id)
        # results = [{"newsId": item.post_id} for item in old_records]
        # return res(success=True, result=results).values()   
    find_record = YouLike.query.filter_by(user_id=user_id, post_id=news_id).first()
    # add item to YouLike table
    # print(f'FIND RECORD.... {(find_record.user_id, find_record.post_id, find_record.createAt)}')
    if not find_record:
        you_like = YouLike(user_id=int(user_id), post_id=int(news_id), createAt=_createAt)
        db.session.add(you_like)
        db.session.commit()
        _collaborative_filtering_update_recommend(session_user_id=user_id, from_post_id=news_id)
        _update_recommend(userId=user_id, postId=news_id)
        return res(success=True,result={"youlikeId": you_like.id}).values()
    return res(success=True).values()

def _update_recommend(userId, postId, recommend_k=6, remove_old=False):
    if remove_old:
        Recommend.query.filter_by(user_id=userId, from_post_id=postId).delete()
        Recommend.query.filter_by(user_id=userId, from_post_id=None).delete()
        db.session.commit()
    
    if not remove_old:
        news_base = Posts.query.filter_by(id=postId).first()
        content_preprocessed = utils.simple_preprocessing(news_base.content)
        bow = id2word.doc2bow(content_preprocessed)
        topics_dist = np.array(
            [doc_top[1] for doc_top in lda_model.get_document_topics(bow=bow, minimum_probability=0.0)]
        )
        most_sims_offsets = distances.get_most_similar_news(topics_dist, np.array(topics_docs_dist), k=int(recommend_k)+1)[1:]
        most_similar_news = []
        for offset in most_sims_offsets:
            news = Posts.query.offset(offset).first()
            most_similar_news.append(Recommend(user_id=userId, post_id=news.id, from_post_id=postId))
        db.session.add_all(most_similar_news)
        db.session.commit()

@bp.route('/detail-by-id', methods=['GET'])
def get_detail_by_id():
    news_id = request.args['newsId']
    news = Posts.query.filter_by(id=news_id).first()
    if news:
        return res(success=True, code=Response.status_code, result={
            "id": news.id,
            "image": news.image,
            "title": news.title,
            "content": news.content,
            "category": news.type
        }).values()
    return res(success=True, code=404, result=None, message="Bài viết không tồn tại").values()

@bp.route('/ban-da-quan-tam', methods=['GET'])
def ban_da_quan_tam():
    user_id = session.get('user_id')
    you_like = Posts.query\
                .join(YouLike, Posts.id==YouLike.post_id)\
                .add_column(YouLike.user_id)\
                .filter_by(user_id=user_id)\
                .all()
    print('YOU LIKE ......... ', you_like)
    result = [
        {
            "id": rec[0].id,
            "title": rec[0].title,
            "image": rec[0].image,
            "type": rec[0].type
        } for rec in you_like
    ]
    return res(success=True, result=result, code=Response.status_code).values()