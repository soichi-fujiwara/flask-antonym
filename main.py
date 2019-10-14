# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import pickle
from io import BytesIO
from gensim.models import KeyedVectors

#対義語生成
import lib_wordRevChange as lw


app = Flask(__name__)

# Main
def picked_up():
    messages = [
        "こんにちは、あなたの名前を入力してください",
        "やあ！お名前は何ですか？",
        "あなたの名前を教えてね"
    ]
    return np.random.choice(messages)

# Routing
@app.route('/', methods=['POST', 'GET'])
def index():
  title = "ようこそ！"
  message = picked_up()

  if request.method == 'POST':

    rev_word = ""
    words = request.form['name']
    name = request.form['name']

    from google.cloud import storage as gcs
    import pandas as pd

    bucket_name = 'ml_bucket_01'
    fname = 'wiki_tohoku_pkl_500000.sav'
    project_name = 'My First Project'

    #プロジェクト名を指定してclientを作成
    client = gcs.Client(project_name)

    #バケット名を指定してbucketを取得
    bucket = client.get_bucket(bucket_name)

    #Blobを作成
    blob = gcs.Blob(fname, bucket)
    #★modelがbytesオブジェクトだと後続でエラーとなる
    content = blob.download_as_string()
    model = KeyedVectors.load(content)

#     model = pickle.loads(pickle.dumps(content))
#     model = pickle.load(open(BytesIO(content), 'rb'))
    
#     #MAIN
#     words = words[0:16]
#     gyaku = u"逆"
#     inherent_words = '[' + words + ']'

#     rev_list = lw.wordRevChange(words,gyaku,inherent_words,model)
#     rev_word = rev_list[1]
    rev_word = type(content)

    return render_template('index.html',message=message,name=name,title=title,rev_word=rev_word)
  else:
    return render_template('index.html',
                           message=message, title=title)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
