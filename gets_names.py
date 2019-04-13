import nltk
import pickle
fake_datums = [[0, "We are currently sitting in Upson Hall people are loud and someone, John Manboy at a really not pleaseant smelling dinner from Mac's Cafe."], [1, "Not only does Seth enjoy dinners from Mac's Cafe, he also reads the newspaper quite frequently. This newspaper is the Cornell Daily Sun."], [2, "Seth Manboy also enjoys volunteering at a local elementary school, South Hill Elementary, on Sundays. He hates frogs."]]   
# data is list lists
# data = [[doc_id, doc], ...]
# later, we may change data to be [[doc_id, desciption, content], ...]
# since the title which is in doc is all capatilized
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

def main():
        get_names(fake_datums)
        print("done")
eval(get_names(fake_datums))
print("done")
