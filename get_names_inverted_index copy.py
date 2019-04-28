import psycopg2
import nltk
import pickle
from collections import Counter
import time
import os

from operator import itemgetter

documents = []
#good_types_to_docs needs to be an inverted index from good types to document ids
good_types_to_docs = {}
def get_ds():
    with open('init_data_structures2.pickle', 'rb') as handle:
        good_types_to_docs = pickle.load(handle)
    handle.close()
get_ds()

#fake_datums = [[0, "We are currently sitting in Upson Hall people are loud and someone, John Manboy at a really not pleaseant smelling dinner from Mac's Cafe."], [1, "Not only does Seth enjoy dinners from Mac's Cafe, he also reads the newspaper quite frequently. This newspaper is the Cornell Daily Sun."], [2, "Seth Manboy also enjoys volunteering at a local elementary school, South Hill Elementary, on Sundays. He hates frogs."]]
# data is list lists
# data = [[doc_id, doc], ...]
# later, we may change data to be [[doc_id, desciption, content], ...]
# since the title which is in doc is all capatilized
hostname = '35.236.208.84'
username = 'postgres'
password = 'dnmSWIMS!'
database = 'postgres'
def connect(topic):
    connection = None
    try:

        connection = psycopg2.connect(
          user = "andreayang",
                                      password = "",
                                      dbname = "andreayang")
        cursor = connection.cursor()

        # Print PostgreSQL Connection properties
        print (connection.get_dsn_parameters(),"\n")
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        #forms list of doc_ids in SQL readable form
        inverted_index_results = good_types_to_docs[topic]
        doc_ids = "(" + str(inverted_index_results[0])
        for doc in inverted_index_results:
            doc_ids = doc_ids + ", " + str(doc)
        doc_ids = doc_ids + ")"

        postgreSQL_select_Query = "select * from articles where doc_id IN " + doc_ids + " LIMIT 1000"
        cursor.execute(postgreSQL_select_Query)
        document_records = cursor.fetchall()

        for row in document_records:
            documents.append([row[0], row[9], row[5]])
        print(documents)
        print("Data read successfully in PostgreSQL ")
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection != None):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
#nltk.download();

# later, we may change data to be [[doc_id, desciption, content], ...]
# since the title which is in doc is all capatilized
def get_names(topic):
    start_time = time.time()
    print("Start time" + str(start_time))
    #people contains all proper nouns from all articles related to the topic queried
    connect(str(topic).lower())
    #documents is now a list of this format [[1, ["Trump", "Mueller"], "https.www"], [8, ["Sarah", "Pittsburgh", "https.www"]]]
    people = []
    for proper_nouns in documents:
        pns = article[1]
        people.append(pns)
    #writing to a file the top 10 most common proper nouns in descending order
    c = Counter(people)
    f = open("name_list.txt","w+")
    most_common_pns = c.most_common(10)
    for name in most_common_pns:
        f.write(name[0])
        f.write("\n")
    f.close()

    links = []
    for pn in most_common_pns:
        good_docs = []
        for doc in documents:
            if(pn in doc[1]):
                good_docs.append(doc)

        doc_scores = []
        for good_doc in good_docs:
            c = Counter(good_doc[1])
            doc_scores.append(good_doc[2], c[pn])

        doc_scores.sort(key=itemgetter(1), reverse = True)
        links.append(doc_scores[0][0])

    print(links)
    execution_time = time.time() - start_time
    documents.clear()
    print("Time to run: " + str(execution_time))

get_names("shooting")
