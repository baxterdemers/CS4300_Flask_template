import json
import requests
import psycopg2
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
import pickle
import parser

hostname = '35.236.208.84'
username = 'postgres'
password = 'dnmSWIMS!'
database = 'postgres'

doc_id = 1
pageSize = 100
pages = 5

good_types_II = defaultdict(list)
person_dict = defaultdict(int)
sw = set(stopwords.words("english"))
good_types_set = set()
persons_set = set()

print("initiating DB connection…")
#myConnection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
myConnection = psycopg2.connect(
          user = "andreayang",
                                      password = "",
                                      dbname = "andreayang")
curr = myConnection.cursor()
print("connected…")

def parse_document(text):
    people_str = ""
    people_lst = []
    tokens = nltk.tokenize.word_tokenize(text) #tokenize to remove punctuation
    token_to_pos = nltk.pos_tag(tokens) #returns list of tuples ([token, pos])
    tagged_tree = nltk.ne_chunk(token_to_pos, binary = False) #tags named entities with PERSON, ORGANIZATION, GPE, etc, returns as a NLTK tree
    for subtree in tagged_tree.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leave in subtree.leaves():
            people_str += "," + leave[0]
            people_lst.append(leave[0])
    return (people_str, people_lst)

def populate_DB(query):
    global doc_id
    data = requests.get("https://newsapi.org/v2/everything?q={}&pageSize={}&page={}&sortBy=relevancy&apiKey=954f0fb443054555a2ed307e8cc1dedd".format(query.strip(), pageSize, 1)).json()
    print("Query: '{}' Status: {}".format(query, data["status"]))
    total_results = data["totalResults"]
    print("Number of results: {}".format(total_results))
    print()
    print()

    results_viewed = 0
    page = 1
    while(results_viewed < total_results and page <= pages):
        print("Topic: {} | Processing page: {}".format(query, page))
        api_url = "https://newsapi.org/v2/everything?q={}&pageSize={}&page={}&sortBy=relevancy&apiKey=954f0fb443054555a2ed307e8cc1dedd".format(query.strip(), pageSize, 1)
        r = requests.get(api_url)
        data = r.json()
        articles = data["articles"]
        for article in articles:
            title = article["title"] if type(article["title"]) == str else ""
            description = article["description"] if type(article["description"]) == str else ""
            content = article["content"] if type(article["content"]) == str else ""
            url = article["url"]
            doc = title + description + content
            source = article["source"]["name"]
            date = article["publishedAt"]
            idx = 0 
            topic = query
            for i,c in enumerate(date):
                if c.isalpha():
                    idx = i
                    break
            clipped_date = date[:idx]
            #people_str, people_lst = parse_document(doc)
            people_str, people_lst = parser.parse_document(doc)
            curr.execute("INSERT INTO articles (doc_id, doc, title, description, content, url, source, date, people) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (doc_id, doc, title, description, content, url, source, clipped_date, people_str))

            if len(people_lst) > 0:
                for person in people_lst:
                    person_dict[person] += 1
                    persons_set.add(person)

            good_types = [token for token in nltk.tokenize.word_tokenize(doc) if token not in sw]
            for term in good_types:
                good_types_II[term].append(doc_id)
                good_types_set.add(term)
            
            doc_id += 1

        page += 1
        results_viewed += pageSize


# topics = ['gun control', 'green new deal', 'data privacy', 'immigration', 'mueller report', 'equal pay'] 
# with open('topics.txt') as f:
#     for line in f:
#         topics.append(line.lower())
topics = ['gun control']

for topic in topics:
    populate_DB(topic)

with open('init_data_structures.pickle', 'wb') as handle:
    pickle.dump(((person_dict, persons_set), (good_types_II, good_types_set)), handle, protocol=pickle.HIGHEST_PROTOCOL)
handle.close()

myConnection.commit()
curr.close()
myConnection.close()