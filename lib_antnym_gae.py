import MeCab
import pandas as pd
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.appengine.api import memcache

def get_cached_data(p_key):
  data = memcache.get(p_key)
  if data is not None:
    return data
  else:
    return None

def get_ant_word(words):
  
  #memcache確認
  if get_cached_data(words) is not None:
    return 
  else:
    # db(FireStore)の初期化
    if (not len(firebase_admin._apps)):
      firebase_admin.initialize_app()

    # db(FireStore)への接続
    db = firestore.Client()

    word_cng_list = []

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

  return ret_list
