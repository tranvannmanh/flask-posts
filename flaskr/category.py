from flask import (
    Blueprint,
    request,
    Response,
    session,
)
from sqlalchemy.sql.expression import func
from . import database
from . import models
import json
from . import dto

bp = Blueprint('category', __name__, url_prefix='/api/category')
Category = models.Category
Posts = models.Posts
Recommend = models.Recommend
db = database.db
res = dto.response.Response

@bp.route('/get-all', methods=['GET'])
def get_all():
    categories = Category.query.all()
    _categories = [{
            "id": item.id, 
            "type": item.type,
            "name": item.name,
            "image": item.image,
            } for item in categories]
    return res(success=True, result=_categories).values()

@bp.route('/generate-recommended', methods=['POST'])
def generate_recommend():
    user_id = session.get('user_id')
    choosed_categories = request.json['choosed_type']
    # print('CHOOSED ...', choosed_categories)
    recommend_record = []
    for category in choosed_categories:
        recommended_by_type = Posts.query\
                                    .filter_by(type=category)\
                                    .order_by(func.random())\
                                    .limit(10).all()
        recommend_record = recommend_record + [Recommend(user_id=user_id, post_id=item.id) for item in recommended_by_type]
        # print('RECOMMENDED.......... ', recommended)
    db.session.add_all(recommend_record)
    db.session.commit()
    return res(success=True).values()

@bp.route('/recommend')
def get_recommend():
    user_id = session.get('user_id')
    page = int(request.args['page'])
    pageItems = int(request.args['pageItems'])

    recommend_record = Posts.query\
                        .join(Recommend, Posts.id==Recommend.post_id)\
                        .add_column(Recommend.user_id)\
                        .filter_by(user_id=user_id)\
                        .order_by(func.random())\
                        .paginate(page=page, per_page=pageItems)
    result = {
        "totalPage": 10,
        "currentPage": page,
        "pageItems": pageItems,
        "data": [{
            "id": item[0].id,
            "title": item[0].title,
            "image": item[0].image,
            "category": item[0].type,
            } for item in recommend_record.items]
    }

    return res(success=True, result=result, code=Response.status_code).values()