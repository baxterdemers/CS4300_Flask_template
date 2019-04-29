import pickle
import numpy as np
import psycopg2
from collections import Counter
import requests

hostname = '35.236.208.84'
username = 'postgres'
password = 'dnmSWIMS!'
database = 'postgres'
names = []
links_dict = {}
title_dict = {}
description_dict = {}

data = requests.get('https://newsapi.org/v2/sources?apiKey=c36e56b19bcc431ca345b8d3f19977d6').json()
sources = set()
for source in data["sources"]:
    sources.add(source["name"].lower())

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
        postgreSQL_select_Query = "select * from production_tbl where doc_id in %(tup_str)s"
        cursor.execute(postgreSQL_select_Query, {'tup_str': tup_str})
        document_records = cursor.fetchall()

        for row in document_records:
            names_list = row[-1].split(',')
            link = row[5]
            title = row[2]
            description = row[3]
            for name in names_list:
                links_dict[name] = link
                title_dict[name] = title
                description_dict[name] = description
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
    doc_id_list = set()
    for word in str(query).lower().split():
        if word in inverted_index:
            if (len(doc_id_list) == 0):
                doc_id_list = set(inverted_index[word])
            else:
                doc_id_list.intersection(set(inverted_index[word]))

    # does not take into account order of rankings
    expanded_words_ranked = query_expansion(query, word_to_index, index_to_word, u)

    for word in expanded_words_ranked:
        if word in inverted_index:
            if (len(doc_id_list) == 0):
                doc_id_list = set(inverted_index[word])
            else:
                doc_id_list.intersection(set(inverted_index[word]))

    return doc_id_list

def get_names_from_doc_ids(doc_ids, query=None):
    if (len(doc_ids) != 0 and query):
        connect(doc_ids)
        c = Counter(names)
        del c['']
        c_top = c.most_common(100)

        for name, name_count in c_top:
            if name.lower() in query.lower() or name.isupper() or name.lower() in sources:
                c[name] = 0

        for name, name_count in c.most_common(100):
            closest_match = ""
            closest_len = 100
            min_occurence_delta = 1000
            match_occurences = 0
            for nmprime,npr_count in c.most_common(100):
                name_prime = nmprime.strip()
                prime_len = len(name_prime.split())
                if name != name_prime and name in name_prime and prime_len <= 2:
                    len_diff = len(name_prime) - len(name)
                    occurence_delta = abs(name_count - npr_count)
                    if occurence_delta < min_occurence_delta:
                        print("true : {} < {}".format(name,name_prime))
                        closest_len = len_diff
                        closest_match = name_prime
                        min_occurence_delta = occurence_delta
                        match_occurences = npr_count
                        
            if closest_match != "":
                print("closest match: {}".format(closest_match))
                if match_occurences/name_count > .25:
                    print("{} gets {} count".format(closest_match, name))
                    c[closest_match] += name_count
                    del c[name]
                else:
                    if name_count < match_occurences:
                        print("{} gets {} count".format(closest_match, name))
                        c[closest_match] += name_count
                        del c[name]
                    else:
                        print("{} gets {} count".format(name, closest_match))
                        c[name] += match_occurences
                        del c[closest_match]

        f = open("name_list.txt","w+")
        for name in c.most_common(20):
            if (name[0] != ""):
                if (name[0][0].isupper()):
                    f.write(name[0])
                    f.write("\n")
        f.close()
        return c
    return Counter()

def create_link_file(doc_id_list, c):
    f = open("link_list.txt","w+")
    for name in c.most_common(20):
        if (name[0] != ""):
            link = links_dict[name[0]]
            f.write(str(link))
            f.write("\n")
    f.close()

def create_title_file(doc_id_list, c):
    f = open("title_list.txt","w+")
    for name in c.most_common(20):
        if (name[0] != ""):
            title = title_dict[name[0]]
            f.write(str(title))
            f.write("\n")
    f.close()

def create_desc_file(doc_id_list, c):
    f = open("desc_list.txt","w+")
    for name in c.most_common(20):
        if (name[0] != ""):
            description = description_dict[name[0]]
            f.write(str(description))
            f.write("\n")
    f.close()

def process_query(inverted_index, word_to_index, index_to_word, u, query=None):
    doc_id_list = get_doc_ids(inverted_index, word_to_index, index_to_word, u, query)
    c = get_names_from_doc_ids(doc_id_list, query)
    create_link_file(doc_id_list, c)
    create_title_file(doc_id_list, c)
    create_desc_file(doc_id_list, c)
    names.clear()
