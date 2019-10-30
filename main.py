# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for

#対義語生成
#import lib_wordRevChange as lw
import lib_antnym as ant


app = Flask(__name__)

# Routing
@app.route('/', methods=['POST', 'GET'])
def index():

  ant_word_list = []
  words = request.form['words'][0:10]

  if request.method == 'POST':

    #対義語取得
    ant_word_list = ant.get_ant_word(words)
    return render_template('index.html',in_words=words,ant_word_list=ant_word_list)
  else:
    #初期表示
    return render_template('index.html',in_words=words,ant_word_list=ant_word_list)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
