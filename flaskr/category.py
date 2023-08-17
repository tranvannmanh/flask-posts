from flask import (
    Blueprint,
    request,
    session
)
from sqlalchemy.sql.expression import func
from . import database
from . import models
import json
from . import dto

bp = Blueprint('category', __name__, url_prefix='/api/category')
Category = models.Category
Posts = models.Posts
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
    # print('categories .... ', [{
    #         "id": item.id, 
    #         "name": item.name,
    #         } for item in categories])
    return res(success=True, result=_categories).values()

@bp.route('/generate-recommended', methods=['POST'])
def generate_recommend():
    user_id = session.get('user_id')
    choosed_categories = request.json['choosed_type']
    print('CHOOSED ...', choosed_categories)
    recommended = []
    for category in choosed_categories:
        recommended_by_type = Posts.query.filter_by(type=category).order_by(func.random()).limit(33).all()
        recommended = recommended + [(user_id, item.id) for item in recommended_by_type]
        # print('RECOMMENDED.......... ', recommended)
    
    return res(success=True).values()