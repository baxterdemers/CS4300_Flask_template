import json
import requests
import psycopg2

hostname = 'localhost'
username = 'andreayang'
password = ''
database = 'andreayang'

pageSize = 100
pages = 10000
topics = ['gun control', 'green new deal', 'data privacy', 'immigration', 'mueller report', 'equal pay'] 

def populate_DB(query):
    data = requests.get("https://newsapi.org/v2/everything?q={}&pageSize={}&page={}&sortBy=relevancy&apiKey=954f0fb443054555a2ed307e8cc1dedd".format(query.strip(), pageSize, 1)).json()
    print("Query: '{}' Status: {}".format(query, data["status"]))
    total_results = data["totalResults"]
    print("Number of results: {}".format(total_results))
    print()
    print()

    results_viewed = 0
    page = 1
    while(results_viewed < total_results and page <= pages):
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
            curr.execute("INSERT INTO articles (doc, title, description, content, url, source, date, topic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (doc, title, description, content, url, source, clipped_date, topic))
        page += 1
        results_viewed += pageSize

print("initiating DB connection…")
myConnection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
curr = myConnection.cursor()
print("connected…")

for topic in topics:
    populate_DB(topic)

myConnection.commit()
curr.close()
myConnection.close()






# query = input("Enter your query: ")
# print()
# print("Article {}:".format(counter))
# print("Title: {}".format(title))
# print("Content: {}".format(content))
# print()
