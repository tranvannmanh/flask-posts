import re
import string
from pyvi import ViTokenizer

stopwords_path = './flaskr/recommender/vietnamese-stopword-dash.txt'

def stopwords(text_file_path=stopwords_path):
    _stopwords = list(open(text_file_path, encoding='utf8').read().split())
    return _stopwords

_stopwords_default = stopwords()
def remove_stopwords(text, stopwords=_stopwords_default):
    return " ".join([word for word in text.split() if word not in stopwords])

def remove_numeric(text):
    table = str.maketrans({key: None for key in string.digits})
    return text.translate(table)

def remove_emails(text):
    return re.sub('\S*@\S*\s?', '', text)

def remove_links(text):
    return re.sub(r"http\S+", "", text)

def remove_multiple_whitespace(text):
    return re.sub("\s\s+", " ", text)

def remove_newline_characters(text):
    return re.sub('\n', ' ', text)

def remove_punctuation(text):
    """https://stackoverflow.com/a/37221663"""
    table = str.maketrans({key: None for key in string.punctuation})
    return text.translate(table)

def vi_tokenizer(text):
    return ViTokenizer.tokenize(text)

def simple_preprocessing(text):
    _text = remove_newline_characters(text)
    _text = remove_emails(_text)
    _text = remove_links(_text)
    _text = remove_numeric(_text)
    _text = remove_punctuation(_text)
    _text = remove_multiple_whitespace(_text)
    _text = vi_tokenizer(_text)
    _text = remove_stopwords(_text)
    return _text


print(simple_preprocessing('abd csjf asjdfl@gmail.com \ns,ndf https:/;sdflsj.com sjdlfj love you http://google.com 843 \n \n 094038 lsjd . =>'))
print('\n\nabd csjf asjdfl@gmail.com \ns,ndf https:/;sdflsj.com sjdlfj love you http://google.com 843 \n \n 094038 lsjd . =>')