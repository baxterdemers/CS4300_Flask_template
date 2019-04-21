import pickle

def get_ds():
    with open('init_data_structures.pickle', 'rb') as handle:
        (person_dict, persons_set), (good_types_II, good_types_set) = pickle.load(handle)
    handle.close()
    return ((person_dict, persons_set), (good_types_II, good_types_set))