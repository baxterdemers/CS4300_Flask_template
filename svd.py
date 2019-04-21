import psycopg2
import nltk
import pickle
from collections import Counter
import os
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
import numpy as np

documents = []

hostname = '35.236.208.84'
username = 'postgres'
password = 'dnmSWIMS!'
database = 'postgres'

def connect():
    connection = None
    try:
        # connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        connection = psycopg2.connect(
          user = "andreayang",
                                      password = "",
                                      dbname = "andreayang")
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        postgreSQL_select_Query = "select * from articles where topic = 'gun control' LIMIT 300"
        cursor.execute(postgreSQL_select_Query)
        document_records = cursor.fetchall()

        print(len(document_records))
        for row in document_records:
            documents.append(row[4])  #append content
            #print("doc_id = ", row[0], )
            #print("content = ", row[4], "\n")
        print("Data read successfully in PostgreSQL ")
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection != None):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

def closest_words(word_in, words_compressed, word_to_index, index_to_word, k = 10):
    if word_in not in word_to_index: return {}
    sims = words_compressed.dot(words_compressed[word_to_index[word_in],:])
    asort = np.argsort(-sims)[:k+1]
    return [(index_to_word[i],sims[i]/sims[asort[0]]) for i in asort[1:]]

def svd():
    connect()
    vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df=.1)
    matrix = vectorizer.fit_transform(documents).transpose()
    #print("matrix shape =", matrix.shape)

    u, s, v_trans = svds(matrix, k=10)
    #print("u shape =", u.shape)
    word_to_index = vectorizer.vocabulary_
    index_to_word = {i:t for t,i in word_to_index.items()}
    u = normalize(u, axis = 1)

    return word_to_index, index_to_word, u

word_to_index, index_to_word, u = svd()

def process_query (query):
    similar_words = {}

    for word in str(query).split():
        result = closest_words(word, u, word_to_index, index_to_word)
        if (len(result) > 0):
            for w, s in result:
                if w not in similar_words:
                    similar_words[w] = s
                else:
                    similar_words[w] += s

    # return a list of similar words ranked by similarity, descending
    ranked = [x[0] for x in sorted(similar_words.items(), key=lambda x:x[1], reverse=True)]
    print(ranked)
    return ranked


