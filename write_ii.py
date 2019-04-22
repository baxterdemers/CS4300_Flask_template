import psycopg2
import nltk
import pickle
from collections import Counter
import os
from nltk.tokenize import RegexpTokenizer

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

        postgreSQL_select_Query = "select * from articles"
        cursor.execute(postgreSQL_select_Query)
        document_records = cursor.fetchall()

        print(len(document_records))
        for row in document_records:
            documents.append([row[0], row[4]])
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

def write_ii():
    connect()
    total_words = Counter()
    words_in_documents = {}
    inverted_index = {}

    for article in documents:
        words = []
        # text = article[1].decode('utf8').strip()
        text = article[1].strip()
        tokens = nltk.tokenize.word_tokenize(text) #tokenize to remove punctuation
        token_to_pos = nltk.pos_tag(tokens) #returns list of tuples ([token, pos])
        for token in token_to_pos:
            total_words[token[0].lower()] += 1
            words.append(token[0].lower())
        words_in_documents[article[0]] = words
    print(total_words)
    print(len(documents))

    bottom_cutoff = 10
    max_value = total_words.most_common(1)[0][1]

    for doc in words_in_documents.items():
        for word in doc[1]:
            if(total_words[word] > bottom_cutoff and float(total_words[word]) / max_value < .4):
                old_list = inverted_index.get(word, [])
                old_list.append(doc[0])
                inverted_index[word] = old_list
    print(inverted_index)

    with open('init_data_structures.pickle', 'wb') as handle:
        pickle.dump(inverted_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

#write_ii()
