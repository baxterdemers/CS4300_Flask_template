import psycopg2
import nltk
import pickle
from collections import Counter
import time
import os
documents = []

#fake_datums = [[0, "We are currently sitting in Upson Hall people are loud and someone, John Manboy at a really not pleaseant smelling dinner from Mac's Cafe."], [1, "Not only does Seth enjoy dinners from Mac's Cafe, he also reads the newspaper quite frequently. This newspaper is the Cornell Daily Sun."], [2, "Seth Manboy also enjoys volunteering at a local elementary school, South Hill Elementary, on Sundays. He hates frogs."]]
# data is list lists
# data = [[doc_id, doc], ...]
# later, we may change data to be [[doc_id, desciption, content], ...]
# since the title which is in doc is all capatilized
def connect(topic):
    connection = None
    try:
        DATABASE_URL = os.environ['DATABASE_URL']

        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        # connection = psycopg2.connect(
        #   user = "nmiwtqndtcgoca",
        #   host = "ec2-54-225-129-101.compute-1.amazonaws.com",
        #                               password = "9f9ffb245f59a92e4daa2c64e671661315a9778b47bbffd1c615f0d1bc113242",
        #                               dbname = "dcvi9pmgc3a8qb")
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        postgreSQL_select_Query = "select * from articles where topic = '" + str(topic) + "' LIMIT 1000"
        cursor.execute(postgreSQL_select_Query)
        document_records = cursor.fetchall()

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
#nltk.download();

# data is list lists
# data = [[doc_id, doc], ...]
# later, we may change data to be [[doc_id, desciption, content], ...]
# since the title which is in doc is all capatilized
def get_names(topic):
    start_time = time.time()
    print("Start time" + str(start_time))
    #people contains all proper nouns from all articles related to the topic queried
    #print("Topic = ", topic)
    connect(str(topic).lower())
    #print("# documents=", len(documents))
    #print(documents[0])
    people = []
    for article in documents:
        text = article[1]
        tokens = nltk.tokenize.word_tokenize(text) #tokenize to remove punctuation
        token_to_pos = nltk.pos_tag(tokens) #returns list of tuples ([token, pos])
        tagged_tree = nltk.ne_chunk(token_to_pos, binary = False) #tags named entities with PERSON, ORGANIZATION, GPE, etc, returns as a NLTK tree
        #print(tagged_tree)
        for subtree in tagged_tree.subtrees(filter=lambda t: t.label() == 'PERSON'):
            for leave in subtree.leaves():
                people.append(leave[0])
                #print ("person=", leave)
    #print(people)
    #print(Counter(people))

    #writing to a file the top 50 most common proper nouns in descending order
    #print("# people found=", len(people))
    c = Counter(people)
    f = open("name_list.txt","w+")
    for name in c.most_common(50):
        f.write(name[0])
        f.write("\n")
    f.close()
    execution_time = time.time() - start_time
    documents.clear()
    print("Time to run: " + str(execution_time))


#TODO don't just pass in documents below, filter the documents for the topic that was queried
#eval(get_names(documents))
#eval(get_names(fake_datums))
print("done")