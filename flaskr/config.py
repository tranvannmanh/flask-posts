from dotenv import load_dotenv
import os
import redis

load_dotenv()

save_path = './flaskr/recommender/models'
PATH_LDA_MODEL = f'{save_path}/LDA.model'
PATH_CORPUS = f'{save_path}/CORPUS.mm'
PATH_TOPICS_DOCS_DIST = f'{save_path}/topics_docs_dist.dat'
PATH_DICTIONARY = f'{save_path}/id2word.dictionary'

class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recommend_system.sqlite'
    SESSION_TYPE="redis",
    SESSION_USE_SIGNER=True,
    SESSION_REDIS=redis.from_url("redis://127.0.0.1:6379")