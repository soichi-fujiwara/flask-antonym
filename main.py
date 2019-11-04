# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
import dask.dataframe as dd

#対義語生成
#import lib_wordRevChange as lw
import lib_antnym_gae as ant


app = Flask(__name__)

# Routing
@app.route('/', methods=['POST', 'GET'])
def index():

  ant_word_list = []

  if request.method == 'POST':

    #対義語取得
    words = request.form['words'][0:12]
    ant_word_list = ant.get_ant_word(words,df_ant)
    return render_template('index.html',in_words=words,ant_word_list=ant_word_list)
  else:
    #初期表示
    words = ""
    return render_template('index.html',in_words=words,ant_word_list=ant_word_list)

if __name__ == '__main__':
    app.debug = True
    csv_dir = 'csv/df_ant_words.csv'
    df_ant = dd.read_csv(csv_dir,header=0, names=('words','ant1','ant2','ant3','flg')).compute()
    app.run(host='0.0.0.0')
