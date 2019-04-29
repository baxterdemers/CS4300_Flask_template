from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import wikipedia
import pickle
import numpy as np
import psycopg2
from collections import Counter, defaultdict

project_name = "Behind The Topic"
net_id = "Sofie Cornelis (sac338), Maya Frai (myf4), Baxter Demers (bld54), Andrea Yang (yy545), Alex Ciampaglia (adc226)"

hostname = '35.236.208.84'
username = 'postgres'
password = 'dnmSWIMS!'
database = 'postgres'
names = []
links_dict = defaultdict(Counter)
title_dict = defaultdict(Counter)
description_dict = defaultdict(Counter)
links_dict
sources = {'the new york times', 'axios', 't3n', 'vice news', 'infomoney', 'marca', 'mtv news (uk)', 'infobae', 'espn', 'football italia', 'msnbc', 'cnn', 'le monde', 'polygon', 'recode', 'the sport bible', 'google news (australia)', 'ign', 'google news (argentina)', 'bild', 'google news (france)', 'the next web', 'newsweek', 'gruenderszene', 'the washington times', 'google news (italy)', 'breitbart news', 'la nacion', 'rtl nieuws', 'wired', 'la gaceta', 'cnbc', 'the irish times', 'entertainment weekly', 'engadget', 'metro', 'der tagesspiegel', 'the lad bible', 'fox sports', 'the american conservative', 'rt', 'espn cric info', 'sabq', 'mtv news', 'fortune', 'google news (israel)', 'göteborgs-posten', 'ynet', 'abc news (au)', 'next big future', 'new scientist', 'the telegraph', 'new york magazine', 'hacker news', 'the huffington post', 'handelsblatt', 'techcrunch', 'business insider', 'national geographic', 'buzzfeed', 'xinhua net', 'ary news', 'nfl news', 'cbc news', 'the wall street journal', 'the times of india', 'fox news', 'argaam', 'google news', 'ars technica', 'globo', 'bbc news', 'medical news today', 'the washington post', 'fourfourtwo', 'google news (canada)', 'focus', 'les echos', 'libération', 'techcrunch (cn)', 'el mundo', 'nrk', 'rbc', 'svenska dagbladet', 'techradar', 'the economist', 'lenta', 'wirtschafts woche', 'national review', 'politico', 'nbc news', 'la repubblica', 'wired.de', 'the globe and mail', 'mashable', 'the hill', 'google news (uk)', 'google news (india)', 'google news (saudi arabia)', 'associated press', 'independent', 'the jerusalem post', 'die zeit', 'financial post', 'usa today', 'ansa.it', 'reddit /r/all', 'il sole 24 ore', 'abc news', 'blasting news (br)', 'bleacher report', 'talksport', 'spiegel online', 'bloomberg', "l'equipe", 'cbs news', 'nhl news', 'time', 'crypto coins news', 'the hindu', 'bbc sport', 'mirror', 'google news (russia)', 'al jazeera english', 'news24', 'daily mail', 'the verge', 'aftenposten', 'cnn spanish', 'google news (brasil)', 'reuters', 'rte', 'news.com.au', 'business insider (uk)', 'australian financial review'}

with open('pickles/inverted_index.pickle', 'rb') as handle:
	inverted_index = pickle.load(handle)

with open('pickles/word_to_index.pickle', 'rb') as handle:
	word_to_index = pickle.load(handle)

with open('pickles/index_to_word.pickle', 'rb') as handle:
	index_to_word = pickle.load(handle)

with open('pickles/u_matrix.pickle', 'rb') as handle:
	u = pickle.load(handle)

def connect(doc_id_lst):
    connection = None
    try:
        connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        record = cursor.fetchone()

        tup_str = tuple(doc_id_lst)
        postgreSQL_select_Query = "select * from articles where doc_id in %(tup_str)s"
        cursor.execute(postgreSQL_select_Query, {'tup_str': tup_str})
        document_records = cursor.fetchall()

        for row in document_records:
            names_list = row[-1].split(',')
            link = row[5]
            title = row[2]
            desc = row[3]
            for name in names_list:
                links_dict[name][link] += 1
                title_dict[name][title] += 1
                description_dict[name][desc] += 1
            names.extend(names_list)

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
            if(connection != None):
                cursor.close()
                connection.close()

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

def get_names_from_doc_ids(doc_ids, query):
    if (len(doc_ids) != 0 and query):
        connect(doc_ids)
        c = Counter(names)
        for word in ['','Share','share', 'Mr.', "Mrs.", "Ms.", "Mueller Time", "Brooks", "Mueller Team Lived", "Technical University", "Democrats", "Democratic", "Representatives", "Republican", "Utah Republican", "Congress", "Senate", "House", "Democratic Republic", "Fiancé Alex Rodriguez", "scrutinyBeto O", "Department", "View"]:
            del c[word]

        c_top = c.most_common(100)
        for name, name_count in c_top:
            words = name.replace('-', ' ').split()
            num_words = len(words)
            num_caps = sum(1 for c in name if c.isupper())
            if (name.lower() in query.lower()) or (name.lower() in sources) or (name.isupper()) or(num_caps > num_words) or (name[0].islower()):
                del c[name]
            if name.strip()[:4] == "Mr. " or name.strip()[:4] == "Ms. ":
                c[name.strip()[4:]] = c[name]
                del c[name]
            if num_words > 3:
                c[name] = int(c[name] / 10)

        for name, name_count in c.most_common(100):
            closest_match = ""
            closest_len = 100
            min_occurence_delta = 1000
            match_occurences = 0
            for nmprime,npr_count in c.most_common(100):
                name_prime = nmprime.strip()
                prime_len = len(name_prime.replace('-', ' ').split())
                if name != name_prime and name in name_prime and prime_len <= 2:
                    len_diff = len(name_prime) - len(name)
                    occurence_delta = abs(name_count - npr_count)
                    if occurence_delta < min_occurence_delta:
                        closest_len = len_diff
                        closest_match = name_prime
                        min_occurence_delta = occurence_delta
                        match_occurences = npr_count
                        
            if closest_match != "":
                if not name_count == 0 and match_occurences/name_count > .25:
                    c[closest_match] += name_count
                    del c[name]
                else:
                    if name_count < match_occurences:
                        c[closest_match] += name_count
                        del c[name]
                    else:
                        c[name] += match_occurences
                        del c[closest_match]

        c_res = c.most_common(100)
        gonzo = set()
        map_g = {}
        for name, name_count in c_res:
            for name2, name_count2 in c_res:
                if name2 not in gonzo and name != name2:
                    proxy_name = name
                    if name in gonzo:
                        loops = 10
                        while proxy_name in gonzo:
                            proxy_name = map_g[proxy_name]
                            name_count = c[proxy_name]
                    nm2_len = len(name2)
                    name_lwr = name.lower()
                    name2_lwr = name2.lower()
                    if name_lwr in name2_lwr and name_lwr != name2_lwr:
                        total = name_count + name_count2
                        if name_lwr == name2_lwr[:(nm2_len-1)]:
                            c[proxy_name] = total
                            del c[name2]
                            gonzo.add(name2)
                            map_g[name2] = proxy_name
                        else:
                            if name_count < name_count2:
                                c[name2] = total
                                del c[proxy_name]
                                gonzo.add(proxy_name)
                                map_g[proxy_name] = name2
                            elif name_count2/(name_count + 1) > .3:
                                c[name2] = total
                                del c[proxy_name]
                                gonzo.add(proxy_name)
                                map_g[proxy_name] = name2
                            else:
                                c[proxy_name] = total
                                del c[name2]
                                gonzo.add(name2)
                                map_g[name2] = proxy_name
        return c
    return Counter()

def process_query(inverted_index, word_to_index, index_to_word, u, query=None):
    if query == None:
        return ([],[],[],[])
    doc_id_list = get_doc_ids(inverted_index, word_to_index, index_to_word, u, query)
    c = get_names_from_doc_ids(doc_id_list, query)
    top_20 = c.most_common(20)
    people_names, links_list, titles_list, desc_list = [""]*20,[""]*20,["No Article Found"]*20,["n/a"]*20
    for idx, (nm, _) in enumerate(top_20):
        people_names[idx] = nm
        try:
            links_list[idx] = links_dict[nm].most_common(1)[0][0]
            titles_list[idx] = title_dict[nm].most_common(1)[0][0]
            desc_list[idx] = description_dict[nm].most_common(1)[0][0]
        except:
            continue
    names.clear()
    return (people_names, links_list, titles_list, desc_list)

# Creating json helper
def make_topics():
	data = {}
	content = wikipedia.page('Wikipedia:List of controversial issues').links

	data["topics"] = content
	file_name = 'data-final.json'
	with open(file_name, 'w') as outfile:
	    json.dump(data, outfile, ensure_ascii=False)

	return file_name

# return list of topics from json data file
def jsonToTopics():
	file_name = make_topics()
	with open(file_name) as json_file:
		data = json.load(json_file)
		topics = data["topics"]
	return topics

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	topics = jsonToTopics()
	people_names, links_list, titles_list, desc_list = process_query(inverted_index, word_to_index, index_to_word, u, query)

	if not query:
		output_message = ''
	else:
		output_message = "Your search: " + query

	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=people_names, links=links_list, topics=topics, titles=titles_list, descriptions=desc_list)
