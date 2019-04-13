from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import wikipedia

project_name = "Behind The Topic"
net_id = "Sofie Cornelis (sac338), Maya Frai (myf4), Baxter Demers (bld54), Andrea Yang (yy545), Alex Ciampaglia (adc226)"

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
	if not query:
		data = []
		output_message = ''
		p_name = ''
		p_link = ''
	else:
		output_message = "Your search: " + query
		data = ["Bernie Sanders", "AOC", "Elizabeth Warren"]
		p_name = "Bernie Sanders"
		p_link = "Link"
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data, person_name=p_name, link=p_link, topics=topics)
