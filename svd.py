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
        connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        postgreSQL_select_Query = "select * from production_tbl"
        cursor.execute(postgreSQL_select_Query)
        document_records = cursor.fetchall()

        print(len(document_records))
        for row in document_records:
            documents.append(row[1])  #append content
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

def svd():
    connect()
    vectorizer = TfidfVectorizer(stop_words = 'english', max_df = .7, min_df=75)
    matrix = vectorizer.fit_transform(documents).transpose()
    print("matrix shape =", matrix.shape)

    u, s, v_trans = svds(matrix, k=10)
    #print("u shape =", u.shape)
    word_to_index = vectorizer.vocabulary_
    index_to_word = {i:t for t,i in word_to_index.items()}
    u = normalize(u, axis = 1)

    with open('word_to_index.pickle', 'wb') as handle:
        pickle.dump(word_to_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('index_to_word.pickle', 'wb') as handle:
        pickle.dump(index_to_word, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    with open('u_matrix.pickle', 'wb') as handle:
        pickle.dump(u, handle, protocol=pickle.HIGHEST_PROTOCOL)

svd()