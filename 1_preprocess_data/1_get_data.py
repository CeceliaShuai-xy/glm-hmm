'''
Author Cecelia Shuai
Created date: 11/29/2023
Purpose: Get Ninad's extracted data & 
            Save a dictionary of each animal
            and its corresponding dir
Last edit time: 11/29/2023
Last edit made:     
'''
import numpy as np
import glob
import numpy.random as npr
import json
from collections import defaultdict
import os
import pdb
npr.seed(65)

if __name__ == '__main__':
    data_path = "/Users/cecelia/Desktop/glm-hmm/data/"
    os.chdir(data_path)
    
    # create directory for saving data:
    if not os.path.exists(data_path + "partially_processed/"):
        os.makedirs(data_path + "partially_processed/")

    if not os.path.exists(data_path + "Subjects/"):
        os.makedirs(data_path + "Subjects/")

    animal_list = os.listdir(data_path + "Subjects/")
    animal_list = [f for f in animal_list if f != '.DS_Store']
    # pdb.set_trace()
    animal_eid_dict = defaultdict(list)
    for animal in animal_list:
        eids = [x[0] for x in os.walk(data_path + "Subjects/" + animal + "/")][1:]
        assert len(eids) > 0, "search in incorrect directory"
        for eid in eids:
            animal_eid_dict[animal].append(eid)

    json = json.dumps(animal_eid_dict)
    f = open("partially_processed/animal_eid_dict.json",  "w")
    f.write(json)
    f.close()
    np.savez('partially_processed/animal_list.npz', animal_list)

