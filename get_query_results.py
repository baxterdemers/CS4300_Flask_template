import pickle
import numpy as np
import psycopg2
from collections import Counter

hostname = '35.236.208.84'
username = 'postgres'
password = 'dnmSWIMS!'
database = 'postgres'
names = []
def connect(doc_id_lst):
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
        
        tup_str = tuple(doc_id_lst)
        postgreSQL_select_Query = "select * from articles where doc_id in %(tup_str)s"
        cursor.execute(postgreSQL_select_Query, {'tup_str': tup_str})
        document_records = cursor.fetchall()

        for row in document_records:
            names_list = row[-1].split(',')
            names.extend(names_list)

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

def query_expansion (query, word_to_index, index_to_word, u):
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
    return ranked

def get_doc_ids (inverted_index, word_to_index, index_to_word, u, query):
    doc_id_list = []
    for word in str(query).lower().split():
        if word in inverted_index:
            doc_id_list.extend(inverted_index[word])

    # does not take into account order of rankings
    expanded_words_ranked = query_expansion(query, word_to_index, index_to_word, u)
    
    for word in expanded_words_ranked:
        if word in inverted_index:
            docs = inverted_index[word]
            doc_id_list.extend(docs)

    return doc_id_list

def get_names_from_doc_ids (doc_ids):
    if (doc_ids != []):
        connect(doc_ids)
        c = Counter(names)
        f = open("name_list.txt","w+")
        for name in c.most_common(20):
            if (name[0] != ""):
                if (name[0][0].isupper()):
                    f.write(name[0])
                    f.write("\n")
        f.close()

def process_query(inverted_index, word_to_index, index_to_word, u, query):
    doc_id_list = get_doc_ids(inverted_index, word_to_index, index_to_word, u, query)
    get_names_from_doc_ids(doc_id_list)
    names.clear()