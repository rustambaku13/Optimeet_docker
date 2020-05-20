# import nltk
import ssl
import ics
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()
# def traverce_tree_up(x):
#     print(x)
#     for i in x.hypernyms():
#         traverce_tree_up(i)
#         print("-------------")
# def traverce_tree_down(x):
#     print(x)
#     for i in x.hyponyms():
#         traverce_tree_down(i)
#         print("-------------")        

# from nltk.corpus import wordnet
# ss = wordnet.synset('workout')
# hyp = lambda s: s.hypernyms()
# print(ss.tree(hyp))
# import nltk
# import nltk
# import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()
['Daily',"Sport","Academic","Work","Recreation"]
from gensim.test.utils import common_texts
from gensim.models import FastText
import gensim.downloader as api
import pandas as pd
from nltk import word_tokenize
from gensim.models import Word2Vec,KeyedVectors
# corpus = api.load('conceptnet-numberbatch-17-06-300',return_path=True)
# print(corpus)
from gensim.models import KeyedVectors
# load the Stanford GloVe model
filename = 'glove.6B.200d.txt.word2vec'
model = KeyedVectors.load_word2vec_format(filename, binary=False)
# calculate: (king - man) + woman = ?
result = model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
print(result)
# a=pd.read_csv('numberbatch-en.txt',delimiter=" ")

# info = api.info()
# json.dumps(info, indent=4)
# for model_name, model_data in sorted(info['models'].items()):
#     print(model_name +  " " + model_data["description"]) 
     

# data = pd.read_csv("Calendar_Events-2.csv")
# data = data.iloc[:,2].values
# data = [word_tokenize(i) for i in data]


# model = FastText(size=4, window=3, min_count=1)

# model.build_vocab(sentences=data)
# model.train(sentences=common_texts, total_examples=data, epochs=10)
