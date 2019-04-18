def parse_document(text):
    people = []
    tokens = nltk.tokenize.word_tokenize(text) #tokenize to remove punctuation
    token_to_pos = nltk.pos_tag(tokens) #returns list of tuples ([token, pos])
    tagged_tree = nltk.ne_chunk(token_to_pos, binary = False) #tags named entities with PERSON, ORGANIZATION, GPE, etc, returns as a NLTK tree
    for subtree in tagged_tree.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leave in subtree.leaves():
            people.append(leave[0])

    return people
