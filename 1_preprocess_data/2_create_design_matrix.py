'''
Author Cecelia Shuai
Created date: 11/29/2023
Purpose: create design matrix for GLM-HMM
Last edit time: 12/17/2023
Last edit made: 9 covariates and 2 dependent variables
'''

'''
INPUT outlook
% Dependent variables
% choice = currrent trial choice = {0,1} 
% reaction time
%         ----------------------------
% Independent variables
% stim = {0, 1} = {vertical, horizontal}
% trialType  = {0, -1, 1} =  {no flanker, incongruent, congruent}
% prevChoice  = {0,1}
% wsls_covariate = {-1, 1} = {stay/shift to vert, stay/shift to horz}
%                   > requires prev choice & prev reward
% flankerContrast [0,8]
% flanker orientation = {0, 1, 2}
% prevType = {0, -1, 1} 
% (?)rewarded = {1, -1} = {rewarded/correct, unrewarded/incorrect}
% prevReward = {-1, 1}
% prevStim = {0, 1} 
'''

import numpy as np
from sklearn.preprocessing import StandardScaler
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
    save_path_cluster = data_path + "data_for_cluster/"
    # Create directories for saving data:
    if not os.path.exists(save_path_cluster):
        os.makedirs(save_path_cluster)

    save_path_individual = save_path_cluster + "data_by_animal/"
    # Create directories for saving data:
    if not os.path.exists(save_path_individual):
        os.makedirs(save_path_individual)

    # Load animal list/results of partial processing:
    animal_list = load_animal_list(
        data_path + 'partially_processed/animal_list.npz')
    animal_eid_dict = load_animal_eid_dict(
        data_path + 'partially_processed/animal_eid_dict.json')

    # Identify idx in master array where each animal's data starts and ends:
    animal_start_idx = {}
    animal_end_idx = {}

# stack all sessions together for each individual animal
    final_animal_eid_dict = defaultdict(list)
    # pdb.set_trace()
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
            save_path_individual + animal +
            '_unnormalized.npz',
            animal_unnormalized_inpt, animal_y,
            animal_session)
        animal_session_fold_lookup = create_train_test_sessions(animal_session,
                                                                3)
        np.savez(
            save_path_individual + animal +
            "_session_fold_lookup" +
            ".npz",
            animal_session_fold_lookup)
        np.savez(
            save_path_individual + animal +
            '_rewarded.npz',
            animal_rewarded)
        assert animal_rewarded.shape[0] == animal_y.shape[0]
        # Now create or append data to master array across all animals:
        if z == 0:
            master_inpt = np.copy(animal_unnormalized_inpt)
            animal_start_idx[animal] = 0
            animal_end_idx[animal] = master_inpt.shape[0] - 1
            master_y = np.copy(animal_y)
            master_session = animal_session
            master_session_fold_lookup_table = animal_session_fold_lookup
            master_rewarded = np.copy(animal_rewarded)
        else:
            animal_start_idx[animal] = master_inpt.shape[0]
            master_inpt = np.vstack((master_inpt, animal_unnormalized_inpt))
            animal_end_idx[animal] = master_inpt.shape[0] - 1
            master_y = np.vstack((master_y, animal_y))
            master_session = np.concatenate((master_session, animal_session))
            master_session_fold_lookup_table = np.vstack(
                (master_session_fold_lookup_table, animal_session_fold_lookup))
            master_rewarded = np.vstack((master_rewarded, animal_rewarded))
    
    # Write out data from across animals
    assert np.shape(master_inpt)[0] == np.shape(master_y)[
        0], "inpt and y not same length"
    assert np.shape(master_rewarded)[0] == np.shape(master_y)[
        0], "rewarded and y not same length"
    assert len(np.unique(master_session)) == \
           np.shape(master_session_fold_lookup_table)[
               0], "number of unique sessions and session fold lookup don't " \
                   "match"

    normalized_inpt = np.copy(master_inpt)

    # pdb.set_trace() # break here to check master_inpt now

    scaler = StandardScaler()
    
    temp = scaler.fit_transform(normalized_inpt)
    # normalized_inpt = temp
    '''
    y = 'Choice(y1) {0,1}'
    x = 
    {'Stim{1,0}','Flanker_ori{1,0}', 
    'FlankerContrast' [0,8],'PrevStim {0,1}', ...
    'PrevChoice {0,1}', 'WSLS' {-1,1}, ...
    'PrevReward'{-1,1}}
    '''
    # pdb.set_trace() 
    # normalize the contrast
    # normalized_inpt[:, 2] = preprocessing.scale(normalized_inpt[:, 2])
    # > edit: only normalize the nonzero element!
    norms = normalized_inpt[:, 2]
    normalized_inpt[:, 2] = np.where(norms!=0,preprocessing.scale(norms),0.) 
    
    # normalize the wsls covariate
    normalized_inpt[:, 5] = preprocessing.scale(normalized_inpt[:, 5])
    # normalize the prevReward
    # normalized_inpt[:,6] = preprocessing.scale(normalized_inpt[:, 6])
    np.savez(save_path_cluster + 'all_animals_concat' + '.npz',
             normalized_inpt,
             master_y, master_session)
    np.savez(
        save_path_cluster + 'all_animals_concat_unnormalized' + '.npz',
        master_inpt, master_y, master_session)
    np.savez(
        save_path_cluster + 'all_animals_concat_session_fold_lookup' +
        '.npz',
        master_session_fold_lookup_table)
    np.savez(save_path_cluster + 'all_animals_concat_rewarded' + '.npz',
             master_rewarded)
    np.savez(save_path_cluster + 'data_by_animal/' + 'animal_list.npz',
             animal_list)

    json = json.dumps(final_animal_eid_dict)
    f = open(save_path_cluster + "final_animal_eid_dict.json", "w")
    f.write(json)
    f.close()

    # Now write out normalized data (when normalized across all animals) for
    # each animal:
    counter = 0
    for animal in animal_start_idx.keys():
        start_idx = animal_start_idx[animal]
        end_idx = animal_end_idx[animal]
        inpt = normalized_inpt[range(start_idx, end_idx + 1)]
        y = master_y[range(start_idx, end_idx + 1)]
        session = master_session[range(start_idx, end_idx + 1)]
        counter += inpt.shape[0]
        np.savez(save_path_cluster + 'data_by_animal/' + animal + '_processed.npz',
                 inpt, y,
                 session)

    assert counter == master_inpt.shape[0]
    
    np.savez(save_path_cluster + 'data_by_animal/' + 'animal_list.npz',
             animal_list)

