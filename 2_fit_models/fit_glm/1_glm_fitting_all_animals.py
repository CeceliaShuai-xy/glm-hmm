'''
Author Cecelia Shuai
Created date: 11/29/2023
Purpose: feed extracted input to GLM with 3-fold CV
Last edit time: 11/29/2023
'''
# Fit GLM to each IBL animal separately
import autograd.numpy as np
import autograd.numpy.random as npr
import os
from glm_utils import load_session_fold_lookup, load_data, load_animal_list, \
    fit_glm, plot_input_vectors, append_zeros
import pdb

npr.seed(65)

C = 2  # number of output types/categories -> vertical, horizontal
N_initializations = 10

if __name__ == '__main__':
    data_dir = '/Users/cecelia/Desktop/glm-hmm/data/data_for_cluster/'
    num_folds = 3

    animal_file = data_dir + 'all_animals_concat.npz'
    inpt, y, session = load_data(animal_file)
    session_fold_lookup_table = load_session_fold_lookup(
        data_dir + 'all_animals_concat_session_fold_lookup.npz')

    results_dir = '/Users/cecelia/Desktop/glm-hmm/results/global_fit/'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Fit GLM to data from single animal:
    for fold in range(num_folds):
        labels_for_plot = [ 'stim', 'trialType', 'prevChoice','wsls', 'flankerContrast', 'bias']
        #
        y = y.astype('int')

        figure_directory = results_dir + "GLM/fold_" + str(fold) + '/'
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)

        # Subset to sessions of interest for fold
        # pdb.set_trace()
        sessions_to_keep = session_fold_lookup_table[np.where(
            session_fold_lookup_table[:, 1] != fold), 0]

        idx_this_fold = [
            str(sess) in sessions_to_keep and y[id, 0] != -1
            for id, sess in enumerate(session)
        ]

        this_inpt, this_y, this_session = inpt[idx_this_fold, :], \
                                            y[idx_this_fold, :], \
                                            session[idx_this_fold]
        
        # Add test data
        sessions_to_test = session_fold_lookup_table[np.where(
            session_fold_lookup_table[:, 1] == fold), 0]
        
        idx_test = [
            str(sess) in sessions_to_test and y[id, 0] != -1
            for id, sess in enumerate(session)
        ]
        test_inpt, test_y, test_session = inpt[idx_test, :], \
                                            y[idx_test, :], \
                                            session[idx_test]

        assert len(
            np.unique(this_y)
        ) == 2, "choice vector should only include 2 possible values"
        train_size = this_inpt.shape[0]

        M = this_inpt.shape[1]
        loglikelihood_train_vector = []

        # pdb.set_trace()
        for iter in range(N_initializations):
            loglikelihood_train, recovered_weights = fit_glm([this_inpt],
                                                                [this_y], M, C)
            weights_for_plotting = append_zeros(recovered_weights) 
            plot_input_vectors(weights_for_plotting,
                                figure_directory,
                                title="GLM fit; Final LL = " +
                                str(loglikelihood_train),
                                save_title='init' + str(iter),
                                labels_for_plot=labels_for_plot)
            loglikelihood_train_vector.append(loglikelihood_train)
            np.savez(
                figure_directory + 'variables_of_interest_iter_' +
                str(iter) + '.npz', loglikelihood_train, recovered_weights)
            
            