import MeCab
import pandas as pd
import numpy as np
import dask.dataframe as dd

def get_ant_word(words):
  
  csv_dir = 'csv/df_ant_words.csv'
  #df_ant = dd.read_csv(csv_dir,header=0, names=('words','ant1','ant2','ant3','flg')).compute()
  df_ant = None
  for tmp in pd.read_csv(csv_dir,header=0, names=('words','ant1','ant2','ant3','flg'),chunksize=10000):
    if df_ant is None:
      df_ant = tmp
    else:
      df_ant = df_ant.append(tmp, ignore_index=True)
  
  word_cng_list = []
  dfTolist = ""
  
  #-------------------------------------------------
  # そのまま対義語化
  #-------------------------------------------------
  dfTolist1 = df_ant[df_ant["words"] == words]["ant1"].values.tolist()
  dfTolist2 = df_ant[df_ant["words"] == words]["ant2"].values.tolist()
  dfTolist3 = df_ant[df_ant["words"] == words]["ant3"].values.tolist()

  dfTolist = dfTolist1 + dfTolist2 + dfTolist3
  #返却値作成
  word_cng_list = word_cng_list.append(dfTolist)
  #◆返却
  yield list(set(word_cng_list))
  #変数クリア
  del dfTolist1
  del dfTolist2
  del dfTolist3
  
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

  #while node:
  for nd in node:
    #分かち書きの単語を取得
    #cut_wd = node.surface
    cut_wd = nd.split("\t")[0]

    #数字はそのまま
    if cut_wd.isnumeric():
      ant_word1 = ant_word1 + str(cut_wd)
      ant_word2 = ant_word2 + str(cut_wd)
      ant_word3 = ant_word3 + str(cut_wd)
    else:      
      if cut_wd != np.nan and cut_wd != '' and cut_wd != 'EOS':
        #if node.feature.split(",")[0] == u"名詞":
        if "\t名詞" in nd:
          try:
            rvs_wd = df_ant[df_ant["words"] == cut_wd].values[0][1]
            if rvs_wd is not np.nan:
              ant_word1 = ant_word1 + str(rvs_wd)
            else:
              ant_word1 = ant_word1 + str(cut_wd)

            rvs_wd = df_ant[df_ant["words"] == cut_wd].values[0][2]
            if rvs_wd is not np.nan:
              ant_word2 = ant_word2 + str(rvs_wd)
            else:
              ant_word2 = ant_word2 + str(cut_wd)

            rvs_wd = df_ant[df_ant["words"] == cut_wd].values[0][3]
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
          #cut_wd = node.feature.split(",")[6]
          cut_wd = nd.split("\t")[0]
          try:
            rvs_wd = df_ant[df_ant["words"] == cut_wd].values[0][1]
            if rvs_wd is not np.nan:
              ant_word1 = ant_word1 + str(rvs_wd)
            else:
              ant_word1 = ant_word1 + str(cut_wd)

            rvs_wd = df_ant[df_ant["words"] == cut_wd].values[0][2]
            if rvs_wd is not np.nan:
              ant_word2 = ant_word2 + str(rvs_wd)
            else:
              ant_word2 = ant_word2 + str(cut_wd)

            rvs_wd = df_ant[df_ant["words"] == cut_wd].values[0][3]
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

    #node = node.next

  word_cng_list.append(ant_word1)
  word_cng_list.append(ant_word2)
  word_cng_list.append(ant_word3)

  del df_ant
  
  #◆返却
  yield list(set(word_cng_list))
