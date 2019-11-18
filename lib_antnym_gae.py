import MeCab
import pandas as pd
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import redis

def decode_utf8(p):
  return p.decode('utf-8')

def get_ant_word(words):
  
  #◆1◆ Cache有の場合はRedisよりデータ取得
  host_name = 'redis-12496.c1.asia-northeast1-1.gce.cloud.redislabs.com'
  port_no = xxxxx
  pass_cd = 'yyyyy'

  try:
    pool = redis.ConnectionPool(host=host_name, port=port_no, password=pass_cd, db=0)
    r = redis.StrictRedis(connection_pool=pool,charset='utf-8', decode_responses=True)
    #Cache data 
    get_data = r.lrange(words, 0, -1)
    rt_list = list(map(decode_utf8, get_data))
    if rt_list != []:
      return rt_list
  except:
    pass

  #◆2◆ Cache無の場合はdb(Firestore)よりデータ取得
  word_cng_list = []
  # dbの初期化
  if (not len(firebase_admin._apps)):
    firebase_admin.initialize_app()

  # dbへの接続
  db = firestore.Client()
  
  #-------------------------------------------------
  # そのまま対義語化
  #-------------------------------------------------
  query = db.collection('nlp').where('words', '==', words)
  docs = query.get()
  for doc in docs:
    word_cng_list.append(doc.to_dict()["ant1"])
    word_cng_list.append(doc.to_dict()["ant2"])
    word_cng_list.append(doc.to_dict()["ant3"])
  
  #-------------------------------------------------
  # 形態素分析後に対義語化
  #-------------------------------------------------
  #tokenizer = MeCab.Tagger("-Ochasen")
  #node = tokenizer.parseToNode(words)
  tokenizer = MeCab.Tagger("")
  node = tokenizer.parse(words).split("\n")
  
  ant_word1 = ''
  ant_word2 = ''
  ant_word3 = ''

  rvs_wd = ''

  for nd in node:
    #分かち書きの単語を取得
    cut_wd = nd.split("\t")[0]

    #数字はそのまま
    if cut_wd.isnumeric():
      ant_word1 = ant_word1 + str(cut_wd)
      ant_word2 = ant_word2 + str(cut_wd)
      ant_word3 = ant_word3 + str(cut_wd)
    else:      
      if cut_wd != np.nan and cut_wd != '' and cut_wd != 'EOS':
        if "\t名詞" in nd:
          try:
            ant_wk_list = []

            query = db.collection('nlp').where('words', '==', cut_wd)
            docs = query.get()

            for doc in docs:
              ant_wk_list.append(doc.to_dict()["ant1"])
              ant_wk_list.append(doc.to_dict()["ant2"])
              ant_wk_list.append(doc.to_dict()["ant3"])

            rvs_wd = ant_wk_list[0]
            if rvs_wd is not np.nan:
              ant_word1 = ant_word1 + str(rvs_wd)
            else:
              ant_word1 = ant_word1 + str(cut_wd)

            rvs_wd = ant_wk_list[1]
            if rvs_wd is not np.nan:
              ant_word2 = ant_word2 + str(rvs_wd)
            else:
              ant_word2 = ant_word2 + str(cut_wd)

            rvs_wd = ant_wk_list[2]
            if rvs_wd is not np.nan:
              ant_word3 = ant_word3 + str(rvs_wd)
            else:
              ant_word3 = ant_word3 + str(cut_wd)

          except IndexError as error:
            #辞書に登録の無い単語の場合
            ant_word1 = ant_word1 + str(cut_wd)
            ant_word2 = ant_word2 + str(cut_wd)
            ant_word3 = ant_word3 + str(cut_wd)

        elif (u"\t動詞" in nd or
          u"\t形容詞" in nd or
          u"\t副詞" in nd or
          u"\t感動詞" in nd):

          #分かち書きの単語を取得
          cut_wd = nd.split("\t")[0]
          try:
            ant_wk_list = []
            
            query = db.collection('nlp').where('words', '==', cut_wd)
            docs = query.get()

            for doc in docs:
              ant_wk_list.append(doc.to_dict()["ant1"])
              ant_wk_list.append(doc.to_dict()["ant2"])
              ant_wk_list.append(doc.to_dict()["ant3"])

            rvs_wd = ant_wk_list[0]
            if rvs_wd is not np.nan:
              ant_word1 = ant_word1 + str(rvs_wd)
            else:
              ant_word1 = ant_word1 + str(cut_wd)

            rvs_wd = ant_wk_list[1]
            if rvs_wd is not np.nan:
              ant_word2 = ant_word2 + str(rvs_wd)
            else:
              ant_word2 = ant_word2 + str(cut_wd)

            rvs_wd = ant_wk_list[2]
            if rvs_wd is not np.nan:
              ant_word3 = ant_word3 + str(rvs_wd)
            else:
              ant_word3 = ant_word3 + str(cut_wd)

          except IndexError as error:
            #辞書に登録の無い単語の場合
            ant_word1 = ant_word1 + str(cut_wd)
            ant_word2 = ant_word2 + str(cut_wd)
            ant_word3 = ant_word3 + str(cut_wd)

        else:
          #◆結合
            ant_word1 = ant_word1 + str(cut_wd)
            ant_word2 = ant_word2 + str(cut_wd)
            ant_word3 = ant_word3 + str(cut_wd)

  word_cng_list.append(ant_word1)
  word_cng_list.append(ant_word2)
  word_cng_list.append(ant_word3)

  #◆返却
  ret_list = list(set(word_cng_list))
  try:
    ret_list.remove(words)
  except ValueError as error:
    pass
  
  if len(ret_list) == 0:
    ret_list = ['該当なし']
  else:
    #Cache Write
    for index in range(len(ret_list)):
      r.rpush(words,str(index))

  return ret_list
