'''
Author Cecelia Shuai
Created date: 11/29/2023
Purpose: create design matrix for GLM-HMM
Last edit time: 11/29/2023
Last edit made: 
'''
## DATA WE WANT
# -------------- DATA WE NEED ---------------
#  y = currrent trial choice
# choice = currrent trial choice
# stim = {1, 2} = {vertical, horizontal}
# flanker = {1, 2}
# flankerContrast (relative) = stim cont - flanker cont 
# rewarded = {1, -1} = {rewarded/correct, unrewarded/incorrect}
# trialType  = {0, 1, 2} =  {no flanker, congruent, incongruent}
# reactionT = reaction time 
# wsls_covariate = {-1, 1} = {stay/shift to vert, stay/shift to horz}
    # requires prev choice & prev reward
# prevType = {0, 1, 2} = {no flanker, congruent, incongruent}

import numpy as np
from sklearn import preprocessing
import numpy.random as npr
import os
import json
from collections import defaultdict
from preprocessing_utils import load_animal_list, load_animal_eid_dict, \
    get_all_unnormalized_data_this_session, create_train_test_sessions
import pdb
npr.seed(65)

if __name__ == '__main__':
    data_path = "/Users/cecelia/Desktop/glm-hmm/data/"
    # Create directories for saving data:
    if not os.path.exists(data_path + "data_by_animal/"):
        os.makedirs(data_path + "data_by_animal/")

    # Load animal list/results of partial processing:
    animal_list = load_animal_list(
        data_path + 'partially_processed/animal_list.npz')
    animal_eid_dict = load_animal_eid_dict(
        data_path + 'partially_processed/animal_eid_dict.json')

# stack all sessions together for each individual animal
    final_animal_eid_dict = defaultdict(list)
    for z, animal in enumerate(animal_list):
        sess_counter = 0
        for eid in animal_eid_dict[animal]:
            animal, unnormalized_inpt, y, session, rewarded = \
                get_all_unnormalized_data_this_session(
                    eid)
            # pdb.set_trace()
            if sess_counter == 0:
                animal_unnormalized_inpt = np.copy(unnormalized_inpt)
                animal_y = np.copy(y)
                animal_session = session
                animal_rewarded = np.copy(rewarded)
            else:
                #pdb.set_trace()
                animal_unnormalized_inpt = np.vstack(
                    (animal_unnormalized_inpt, unnormalized_inpt))
                animal_y = np.vstack((animal_y, y))
                animal_session = np.concatenate((animal_session, session))
                animal_rewarded = np.vstack((animal_rewarded, rewarded))
            sess_counter += 1
            final_animal_eid_dict[animal].append(eid)
        # Write out animal's unnormalized data matrix:
        np.savez(
            data_path + 'data_by_animal/' + animal +
            '_unnormalized.npz',
            animal_unnormalized_inpt, animal_y,
            animal_session)
        animal_session_fold_lookup = create_train_test_sessions(animal_session,
                                                                3)
        np.savez(
            data_path + 'data_by_animal/' + animal +
            "_session_fold_lookup" +
            ".npz",
            animal_session_fold_lookup)
        np.savez(
            data_path + 'data_by_animal/' + animal +
            '_rewarded.npz',
            animal_rewarded)
        assert animal_rewarded.shape[0] == animal_y.shape[0]
    # master list that include all animals' data is omitte here
    
    np.savez(data_path + 'data_by_animal/' + 'animal_list.npz',
             animal_list)

    json = json.dumps(final_animal_eid_dict)
    f = open(data_path + "final_animal_eid_dict.json", "w")
    f.write(json)
    f.close()

