import MeCab
import pandas as pd
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import redis

#-----------------------------------------------------------------------------------------
# correction_sentence
#-----------------------------------------------------------------------------------------
def correction_sentence(p_str):
  
  p_str = p_str.replace('めるられました','られました')
  p_str = p_str.replace('るさせるた','らせた')
  p_str = p_str.replace('めるられた','られた')
  p_str = p_str.replace('るました','ました')
  p_str = p_str.replace('しいない','しくない')
  p_str = p_str.replace('しいます','しいです')
  p_str = p_str.replace('るない','ない')
  p_str = p_str.replace('るます','ます')
  p_str = p_str.replace('きるな','きな')
  p_str = p_str.replace('るた','った')

  return p_str

#-----------------------------------------------------------------------------------------
# decode_utf8
#-----------------------------------------------------------------------------------------
def decode_utf8(p):
  return p.decode('utf-8')

#-----------------------------------------------------------------------------------------
# create_antonym_strings
#-----------------------------------------------------------------------------------------
def create_antonym_strings(p_cut_wd,p_ant_wk_list,p_ant_word1,p_ant_word2,p_ant_word3):

  # Delete from Instr = Antonym
  try:
    rvs_wd = p_ant_wk_list[0]
    if rvs_wd is not np.nan:
      p_ant_word1 = p_ant_word1 + str(rvs_wd)
    else:
      p_ant_word1 = p_ant_word1 + str(p_cut_wd)
  except:
    p_ant_word1 = p_ant_word1 + str(p_cut_wd)

  try:
    rvs_wd = p_ant_wk_list[1]
    if rvs_wd is not np.nan:
      p_ant_word2 = p_ant_word2 + str(rvs_wd)
    else:
      p_ant_word2 = p_ant_word2 + str(p_cut_wd)
  except:
    p_ant_word2 = p_ant_word2 + str(p_cut_wd)

  try:
    rvs_wd = p_ant_wk_list[2]
    if rvs_wd is not np.nan:
      p_ant_word3 = p_ant_word3 + str(rvs_wd)
    else:
      p_ant_word3 = p_ant_word3 + str(p_cut_wd)
  except:
    p_ant_word3 = p_ant_word3 + str(p_cut_wd)

  rslt_list = []
  rslt_list.append(p_ant_word1)
  rslt_list.append(p_ant_word2)
  rslt_list.append(p_ant_word3)

  return rslt_list

#-----------------------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------------------
def get_ant_word(words):
  
  word_cng_list = []

  #-----------------------------------------------------------------------------------------
  # Redis Connect
  #-----------------------------------------------------------------------------------------
  host_name = 'xxxxx'
  port_no = yyyyy
  pass_cd = 'zzzzz'

  try:
    pool = redis.ConnectionPool(host=host_name, port=port_no, password=pass_cd, db=0)
    r = redis.StrictRedis(connection_pool=pool,charset='utf-8', decode_responses=True)
  except:
    pass

  #-----------------------------------------------------------------------------------------
  # Firestore Connect
  #-----------------------------------------------------------------------------------------
  # dbの初期化
  if (not len(firebase_admin._apps)):
    firebase_admin.initialize_app()

  # dbへの接続
  db = firestore.Client()
  
  #-------------------------------------------------
  # ◆1. 形態素分析後に対義語化
  #-------------------------------------------------
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
            cache_write_list = []

            #------------------------------------------------------------------
            # ◆Get Cache Data
            #------------------------------------------------------------------
            get_data = r.lrange(cut_wd, 0, -1)
            rt_list = list(map(decode_utf8, get_data))

            if rt_list == []:
              #------------------------------------------------------------------
              # Get Firestore DB
              #------------------------------------------------------------------
              query = db.collection('nlp').where('words', '==', cut_wd)
              docs = query.get()

              for doc in docs:
                wk = doc.to_dict()["ant1"]
                ant_wk_list.append(wk)
                cache_write_list.append(wk)
                wk = doc.to_dict()["ant2"]
                ant_wk_list.append(wk)
                cache_write_list.append(wk)
                wk = doc.to_dict()["ant3"]
                ant_wk_list.append(wk)
                cache_write_list.append(wk)

              #------------------------------------------------------------------
              # ◆Write Redis Cache
              #------------------------------------------------------------------
              try:
                for index in range(len(cache_write_list)):
                  r.rpush(cut_wd,str(cache_write_list[index]))
              except:
                pass

            else:
              #------------------------------------------------------------------
              # Set Cache Data
              #------------------------------------------------------------------
              for lst in rt_list:
                ant_wk_list.append(lst)

            #-------------------------------------------------------------------
            # create antonym strings
            #-------------------------------------------------------------------
            rt_list2 = create_antonym_strings(cut_wd,ant_wk_list,ant_word1,ant_word2,ant_word3)
            ant_word1 = rt_list2[0]
            ant_word2 = rt_list2[1]
            ant_word3 = rt_list2[2]
            
          # DB Error ?
          except:
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
            cache_write_list = []
            
            #------------------------------------------------------------------
            # ◆Get Cache Data
            #------------------------------------------------------------------
            get_data = r.lrange(cut_wd, 0, -1)
            rt_list = list(map(decode_utf8, get_data))

            if rt_list == []:
              #------------------------------------------------------------------
              # Get Firestore DB
              #------------------------------------------------------------------
              query = db.collection('nlp').where('words', '==', cut_wd)
              docs = query.get()

              for doc in docs:
                wk = doc.to_dict()["ant1"]
                ant_wk_list.append(wk)
                cache_write_list.append(wk)
                wk = doc.to_dict()["ant2"]
                ant_wk_list.append(wk)
                cache_write_list.append(wk)
                wk = doc.to_dict()["ant3"]
                ant_wk_list.append(wk)
                cache_write_list.append(wk)

              #------------------------------------------------------------------
              # ◆Write Cache Data
              #------------------------------------------------------------------
              try:
                for index in range(len(cache_write_list)):
                  r.rpush(cut_wd,str(cache_write_list[index]))
              except:
                pass

            else:
              #------------------------------------------------------------------
              # Set Redis Cache
              #------------------------------------------------------------------
              for lst in rt_list:
                ant_wk_list.append(lst)

            #-------------------------------------------------------------------
            # create antonym strings
            #-------------------------------------------------------------------
            rt_list2 = create_antonym_strings(cut_wd,ant_wk_list,ant_word1,ant_word2,ant_word3)
            ant_word1 = rt_list2[0]
            ant_word2 = rt_list2[1]
            ant_word3 = rt_list2[2]

          # DB Error ?
          except:
            ant_word1 = ant_word1 + str(cut_wd)
            ant_word2 = ant_word2 + str(cut_wd)
            ant_word3 = ant_word3 + str(cut_wd)

        else:
          #特定の動名詞etc 以外
          ant_word1 = ant_word1 + str(cut_wd)
          ant_word2 = ant_word2 + str(cut_wd)
          ant_word3 = ant_word3 + str(cut_wd)
          
  #Return Data
  word_cng_list.append(correction_sentence(ant_word1))
  word_cng_list.append(correction_sentence(ant_word2))
  word_cng_list.append(correction_sentence(ant_word3))
  #-------------------------------------------------
  # ◆2. そのまま対義語化
  #-------------------------------------------------
  # Get Cache Data
  #------------------------------------------------------------------
  try:
    get_data = r.lrange(words, 0, -1)
    rt_list = list(map(decode_utf8, get_data))

    cache_write_list = []
    
    if rt_list == []:
      #------------------------------------------------------------------
      # Get Firestore DB
      #------------------------------------------------------------------
      query = db.collection('nlp').where('words', '==', words)
      docs = query.get()

      for doc in docs:
        wk = doc.to_dict()["ant1"]
        word_cng_list.append(wk)
        cache_write_list.append(wk)
        wk = doc.to_dict()["ant2"]
        word_cng_list.append(wk)
        cache_write_list.append(wk)
        wk = doc.to_dict()["ant3"]
        word_cng_list.append(wk)
        cache_write_list.append(wk)

      #------------------------------------------------------------------
      # Write Redis Cache
      #------------------------------------------------------------------
      try:
        for index in range(len(cache_write_list)):
          r.rpush(words,str(cache_write_list[index]))
      except:
        pass

    else:
      #------------------------------------------------------------------
      # Get Redis Cache
      #------------------------------------------------------------------
      for lst in rt_list:
        word_cng_list.append(lst)
  except:
    pass

  #Return Data
  ret_list = list(set(word_cng_list))
  try:
    ret_list.remove(words)
  except ValueError as error:
    pass
  
  ret_list_fix = []
  for rlst in ret_list:
    ret_list_fix.append(rlst.replace('@',''))
  
  if len(ret_list_fix) == 0:
    ret_list_fix = ['該当なし']

  ant_word1 = ''
  ant_word2 = ''
  ant_word3 = ''
  get_data = ''
  cache_write_list = []
  word_cng_list = []
  ret_list = []
  
  return ret_list_fix
