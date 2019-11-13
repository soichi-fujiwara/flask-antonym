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

  ant_word_list = []
  if request.method == 'POST':

    #参考値作成
    auto_comp_list = ['(例)好きなジブリ映画',
                      '(例)好きな観光地',
                      '(例)好きな小説',
                      '(例)好きなドラマ',
                      '(例)流行りの言葉',
                      '(例)好きな店の名前',
                      '(例)気になる学校の名前',
                      '(例)キャラクターの名前',
                      '(例)好きな曲名',
                      '(例)好きなお菓子',
                      '(例)好きなフレーズ',
                      '(例)想い出の場所']

    auto_comp = auto_comp_list[random.randint(0,12)]

    #対義語取得
    words = request.form['words'][0:12]
    ant_word_list = ant.get_ant_word(words)
    return render_template('index.html',auto_comp=auto_comp,in_words=words,ant_word_list=ant_word_list)
  else:
    #初期表示
    words = ""
    auto_comp = "単語や文章を入力して下さい"
    return render_template('index.html',auto_comp=auto_comp,in_words=words,ant_word_list=ant_word_list)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
