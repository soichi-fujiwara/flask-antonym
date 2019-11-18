# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
import random

#対義語生成
#import lib_wordRevChange as lw
import lib_antnym_gae as ant


app = Flask(__name__)

# Routing
@app.route('/', methods=['POST', 'GET'])
def index():

  auto_comp = "単語や文章を入力して下さい"

  ant_word_list = []
  if request.method == 'POST':

    #対義語取得
    words = request.form['words'][0:12].replace(' ','').replace('　','')
    ant_word_list = ant.get_ant_word(words)
    return render_template('index.html',auto_comp=auto_comp,in_words=words,ant_word_list=ant_word_list)
  else:
    #初期表示
    words = ""
    return render_template('index.html',auto_comp=auto_comp,in_words=words,ant_word_list=ant_word_list)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
