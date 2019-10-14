import MeCab
#括弧記号無効化
import lib_delete_brackets

def search_similar_texts(p_words):
  pass

def wordRevChange(words,gyaku,inherent_words,model):

  word_cng_list = []

  #**************************************************************************
  #そのまま対義化
  #**************************************************************************
  asitis_cng_words1 = ''
  asitis_cng_words2 = ''
  try:
    for i in range(5):
      rvs_wd = model.most_similar(positive=[inherent_words,gyaku])[i][0]
      if inherent_words.replace('[',"").replace(']',"") != rvs_wd.replace('[',"").replace(']',""):
        asitis_cng_words1 = model.most_similar(positive=[inherent_words,gyaku])[i][0]
        asitis_cng_words2 = model.most_similar(positive=[inherent_words,gyaku])[i+1][0]
        break
      else:
        asitis_cng_words = words
  except KeyError as error:
    #辞書に登録の無い単語の場合
    search_similar_texts(inherent_words)

  #**************************************************************************
  #形態素分析後に対義化
  #**************************************************************************
  tokenizer = MeCab.Tagger("-Ochasen")
  node = tokenizer.parseToNode(words)

  while node:
    cut_wd = node.surface

    if node.feature.split(",")[0] == u"名詞":
      try:
        for i in range(5):
          rvs_wd = model.most_similar(positive=[cut_wd,gyaku])[i][0]
          if cut_wd != rvs_wd.replace('[',"").replace(']',""):
            #◆結合
            word_cng_list.append(rvs_wd.replace('[',"").replace(']',""))
            break
      except KeyError as error:
        #辞書に登録の無い単語の場合
        search_similar_texts(cut_wd)

    elif node.feature.split(",")[0] == u"形容詞":
      cut_wd = node.feature.split(",")[6]

      try:
        for i in range(5):
          rvs_wd = model.most_similar(positive=[cut_wd,gyaku])[i][0]
          if cut_wd != rvs_wd.replace('[',"").replace(']',""):
            #◆結合
            word_cng_list.append(rvs_wd.replace('[',"").replace(']',""))
            break
      except KeyError as error:
        #辞書に登録の無い単語の場合
        search_similar_texts(cut_wd)

    elif node.feature.split(",")[0] == u"動詞":
      cu_wd = node.feature.split(",")[6]

      try:
        for i in range(5):
          rvs_wd = model.most_similar(positive=[cut_wd,gyaku])[i][0]
          if cut_wd != rvs_wd.replace('[',"").replace(']',""):
            #◆結合
            word_cng_list.append(rvs_wd.replace('[',"").replace(']',""))
            break
      except KeyError as error:
        #辞書に登録の無い単語の場合
        search_similar_texts(cut_wd)

    else:
      #◆結合
      word_cng_list.append(cut_wd.replace('[',"").replace(']',""))

    node = node.next

  asitis_cng_words1 = asitis_cng_words1.replace('[',"").replace(']',"").replace('_',"")
  asitis_cng_words2 = asitis_cng_words2.replace('[',"").replace(']',"").replace('_',"")

  result_list = []

  result_list.append(words)
  result_list.append(lib_delete_brackets.delete_brackets(asitis_cng_words1))
  result_list.append(lib_delete_brackets.delete_brackets(asitis_cng_words2))
  result_list.append(''.join(word_cng_list))

  return result_list
