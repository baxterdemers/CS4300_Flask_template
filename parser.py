def parse_document(text):
    people = []
    tokens = nltk.tokenize.word_tokenize(text) #tokenize to remove punctuation
    token_to_pos = nltk.pos_tag(tokens) #returns list of tuples ([token, pos])
    tagged_tree = nltk.ne_chunk(token_to_pos) #tags named entities with PERSON, ORGANIZATION, GPE, etc, returns as a NLTK tree
#     print(tagged_tree)
    for subtree in tagged_tree.subtrees(filter=lambda t: t.label() in ['PERSON', 'ORGANIZATION']):
#         print(subtree)
        entity = ""
        for leave in subtree.leaves():
#             print(leave)
            entity = entity + " " + leave[0]
        people.append(entity.strip())  #strip to remove space before name
#         print()

    return people
