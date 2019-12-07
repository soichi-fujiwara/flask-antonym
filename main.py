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
    #1回目
    words = request.form['words'][0:12].replace(' ','').replace('　','')
    ant_word_list = ant.get_ant_word(words)
    
    #2回目
    words_2 = words
    tokenizer = MeCab.Tagger("")
    if ant_word_list == ['該当なし']:
      for num in range(2,len(words)-2):
        node = tokenizer.parse(words[num:]).split("\n")
        for nd in node:
          #表層形(IN)=発音が一致する → 辞書に単語登録がある可能性が高い性質を利用
          # 表層形(IN) : words[num:]
          # 発音       : nd.split(',')[-1] (最終項目)
          if words[num:] == nd.split(',')[-1]:
            words_2 = words[0:num] + '@' + words[num:]
            break

      if words_2 != words: 
        ant_word_list = replace(ant.get_ant_word(words),'@','')
      
    return render_template('index.html',auto_comp=auto_comp,in_words=words,ant_word_list=ant_word_list)
  else:
    #初期表示
    words = ""
    return render_template('index.html',auto_comp=auto_comp,in_words=words,ant_word_list=ant_word_list)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',threaded=True)
