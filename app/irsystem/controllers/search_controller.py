from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import wikipedia
import get_names

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

	# get list of topics for auto-complete
	topics = jsonToTopics()

	# call people parsing function to get list of people's names
	#get_names.connect(query)
	get_names.get_names(query)

	if not query:
		people_names = []
		output_message = ''
		p_name = ''
		p_link = ''
	else:
		people_names = []
		output_message = "Your search: " + query
		# data = ["Bernie Sanders", "AOC", "Elizabeth Warren"]
		with open('name_list.txt') as f:
			for line in f:
					people_names.append(line)

		p_name = "Bernie Sanders"
		p_link = "Link"
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=people_names, person_name=p_name, link=p_link, topics=topics)