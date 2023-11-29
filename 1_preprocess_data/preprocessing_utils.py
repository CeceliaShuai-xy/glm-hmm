# NOTICE: modified version 
'''
Author Cecelia Shuai
Created date: 11/29/2023
Purpose: modified util function
Last edit time: 11/29/2023
Last edit made: 
'''
import numpy as np
import numpy.random as npr
from scipy.stats import bernoulli
import scipy.io as sio
import json
import os
from oneibl.onelight import ONE

one = ONE()


def get_animal_name(eid):
    # get session id:
    raw_session_id = eid.split('Subjects/')[1]
    # Get animal:
    animal = raw_session_id.split('/')[0]
    return animal


def get_raw_data(eid):
    print(eid)
    # get session id:
    raw_session_id = eid.split('Subjects/')[1]
    # Get animal:
    animal = raw_session_id.split('/')[0]
    # replace '/' with dash in session ID
    session_id = raw_session_id.replace('/', '-')
    

    current_dir = os.getcwd()
    os.chdir(eid)

    # Get choice, stim & flanker data and rewarded/not rewarded:
    choice = sio.loadmat(eid + '/choice.mat')["choice"]
    stim = sio.loadmat(eid + '/stim.mat')["stim"]
    flanker = sio.loadmat(eid + '/flanker.mat')["flanker"]
    flanker_contrast = sio.loadmat(eid + '/flankerContrast.mat')["flankerContrast"]
    rewarded = sio.loadmat(eid + '/rewarded.mat')["rewarded"]
    trialType = sio.loadmat(eid + '/trialType.mat')["trialType"]
    reactionT = sio.loadmat(eid + '/reactionT.mat')["reactionT"]
    wsls = sio.loadmat(eid + '/wsls.mat')["wsls"]
    prevType = sio.loadmat(eid + '/prevType.mat')["prevType"]
    prevChoice = sio.loadmat(eid + '/prevChoice.mat')["prevChoice"]

    os.chdir(current_dir)
    return animal, session_id, choice, stim, flanker, flanker_contrast,\
          rewarded, trialType, reactionT, wsls, prevType, prevChoice


def create_stim_vector(stim_left, stim_right):
    # want stim_right - stim_left
    # Replace NaNs with 0:
    stim_left = np.nan_to_num(stim_left, nan=0)
    stim_right = np.nan_to_num(stim_right, nan=0)
    # now get 1D stim
    signed_contrast = stim_right - stim_left
    return signed_contrast


# def create_previous_choice_vector(choice):
#     ''' choice: choice vector of size T
#         previous_choice : vector of size T with previous choice made by
#         animal - output is in {0, 1}, where 0 corresponds to a previous left
#         choice; 1 corresponds to right.
#         If the previous choice was a violation, replace this with the choice
#         on the previous trial that was not a violation.
#         locs_mapping: array of size (~num_viols)x2, where the entry in
#         column 1 is the location in the previous choice vector that was a
#         remapping due to a violation and the
#         entry in column 2 is the location in the previous choice vector that
#         this location was remapped to
#     '''
#     previous_choice = np.hstack([np.array(choice[0]), choice])[:-1]
#     locs_to_update = np.where(previous_choice == -1)[0]
#     locs_with_choice = np.where(previous_choice != -1)[0]
#     loc_first_choice = locs_with_choice[0]
#     locs_mapping = np.zeros((len(locs_to_update) - loc_first_choice, 2),
#                             dtype='int')

#     for i, loc in enumerate(locs_to_update):
#         if loc < loc_first_choice:
#             # since no previous choice, bernoulli sample: (not output of
#             # bernoulli rvs is in {1, 2})
#             previous_choice[loc] = bernoulli.rvs(0.5, 1) - 1
#         else:
#             # find nearest loc that has a previous choice value that is not
#             # -1, and that is earlier than current trial
#             potential_matches = locs_with_choice[
#                 np.where(locs_with_choice < loc)]
#             absolute_val_diffs = np.abs(loc - potential_matches)
#             absolute_val_diffs_ind = absolute_val_diffs.argmin()
#             nearest_loc = potential_matches[absolute_val_diffs_ind]
#             locs_mapping[i - loc_first_choice, 0] = int(loc)
#             locs_mapping[i - loc_first_choice, 1] = int(nearest_loc)
#             previous_choice[loc] = previous_choice[nearest_loc]
#     assert len(np.unique(
#         previous_choice)) <= 2, "previous choice should be in {0, 1}; " + str(
#         np.unique(previous_choice))
#     return previous_choice, locs_mapping


# def create_wsls_covariate(previous_choice, success, locs_mapping):
#     '''
#     inputs:
#     success: vector of size T, entries are in {-1, 1} and 0 corresponds to
#     failure, 1 corresponds to success
#     previous_choice: vector of size T, entries are in {0, 1} and 0
#     corresponds to left choice, 1 corresponds to right choice
#     locs_mapping: location remapping dictionary due to violations
#     output:
#     wsls: vector of size T, entries are in {-1, 1}.  1 corresponds to
#     previous choice = right and success OR previous choice = left and
#     failure; -1 corresponds to
#     previous choice = left and success OR previous choice = right and failure
#     '''
#     # remap previous choice vals to {-1, 1}
#     remapped_previous_choice = 2 * previous_choice - 1
#     previous_reward = np.hstack([np.array(success[0]), success])[:-1]
#     # Now need to go through and update previous reward to correspond to
#     # same trial as previous choice:
#     for i, loc in enumerate(locs_mapping[:, 0]):
#         nearest_loc = locs_mapping[i, 1]
#         previous_reward[loc] = previous_reward[nearest_loc]
#     wsls = previous_reward * remapped_previous_choice
#     assert len(np.unique(wsls)) == 2, "wsls should be in {-1, 1}"
#     return wsls


# def remap_choice_vals(choice):
#     # raw choice vector has CW = 1 (correct response for stim on left),
#     # CCW = -1 (correct response for stim on right) and viol = 0.  Let's
#     # remap so that CW = 0, CCw = 1, and viol = -1
#     choice_mapping = {1: 0, -1: 1, 0: -1}
#     new_choice_vector = [choice_mapping[old_choice] for old_choice in choice]
#     return new_choice_vector


def create_design_mat(stim, flanker, flanker_contrast,\
          rewarded, trialType, reactionT, wsls, prevType, prevChoice):
    
    # Create unnormalized_inpt
    # with first column = stim_right - stim_left,
    # second column as past choice, third column as WSLS
    
    T = stim.shape[1]
    design_mat = np.zeros((T, 9))
    design_mat[:, 0] = stim
    design_mat[:, 1] = flanker
    design_mat[:, 2] = flanker_contrast
    design_mat[:, 3] = rewarded
    design_mat[:, 4] = trialType
    design_mat[:, 5] = reactionT
    design_mat[:, 6] = wsls
    design_mat[:, 7] = prevType
    design_mat[:, 8] = prevChoice
    return design_mat


def get_all_unnormalized_data_this_session(eid):
    # Load raw data
    animal, session_id, choice, stim, flanker, flanker_contrast,\
          rewarded, trialType, reactionT, wsls, prevType, prevChoice \
        = get_raw_data(eid)
    
 
    # Create design mat = matrix of size T x 9
    unnormalized_inpt = create_design_mat(stim, flanker, \
                                        flanker_contrast, rewarded, \
                                        trialType, reactionT, wsls, \
                                        prevType, prevChoice)
    # y = np.expand_dims(choice, axis=1)
    y = choice.reshape(-1,1)
    session = [session_id for i in range(y.shape[0])]
    rewarded = rewarded.reshape(-1,1)

    return animal, unnormalized_inpt, y, session, rewarded


def load_animal_list(file):
    container = np.load(file, allow_pickle=True)
    data = [container[key] for key in container]
    animal_list = data[0]
    return animal_list


def load_animal_eid_dict(file):
    with open(file, 'r') as f:
        animal_eid_dict = json.load(f)
    return animal_eid_dict


def load_data(animal_file):
    container = np.load(animal_file, allow_pickle=True)
    data = [container[key] for key in container]
    inpt = data[0]
    y = data[1]
    y = y.astype('int')
    session = data[2]
    return inpt, y, session


def create_train_test_sessions(session, num_folds=3):
    # create a session-fold lookup table
    num_sessions = len(np.unique(session))
    # Map sessions to folds:
    unshuffled_folds = np.repeat(np.arange(num_folds),
                                 np.ceil(num_sessions / num_folds))
    shuffled_folds = npr.permutation(unshuffled_folds)[:num_sessions]
    assert len(np.unique(
        shuffled_folds)) == num_folds, "require at least one session per fold for " \
                               "each animal!"
    # Look up table of shuffle-folds:
    sess_id = np.array(np.unique(session), dtype='str')
    shuffled_folds = np.array(shuffled_folds, dtype='O')
    session_fold_lookup_table = np.transpose(
        np.vstack([sess_id, shuffled_folds]))
    return session_fold_lookup_table
