import psycopg2
import nltk
import pickle
documents = []
# data is list lists
# data = [[doc_id, doc], ...]
# later, we may change data to be [[doc_id, desciption, content], ...]
# since the title which is in doc is all capatilized

try:
    connection = psycopg2.connect(
								  user = "postgres",
                                  password = "alexdaniel",
                                  dbname = "prototype")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")
    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")

	postgreSQL_select_Query = "select * from mobile"
    cursor.execute(postgreSQL_select_Query)
    document_records = cursor.fetchall()

    for row in document_records:
	    documents.append([row[0], row[4]])
        print("doc_id = ", row[0], )
        print("content = ", row[4]) "\n")
    print("Data read successfully in PostgreSQL ")
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

nltk.download();
def get_names(data):
	for article in data:
                text = article[1]
		# https://stackoverflow.com/questions/19494449/parse-text-to-get-the-proper-nouns-names-and-organizations-python-nltk
		tokens = nltk.tokenize.word_tokenize(text) #tokenize to remove punctuation
		token_to_pos = nltk.pos_tag(tokens) #returns list of tuples ([token, pos])
		tagged_tree = nltk.ne_chunk(token_to_pos, binary = False) #tags named entities with PERSON, ORGANIZATION, GPE, etc, returns as a NLTK tree
		print tagged_tree
		people = []
		for subtree in tagged_tree.subtrees(filter=lambda t: t.label() == 'PERSON'):
                        for leave in subtree.leaves():
                            people.append(leave)
                            print ("person=", leave)
eval(get_names(fake_datums))
print("done")
