# Plot overall accuracy of animal, as well as its accuracy in each of the
# three states
import json
import sys
import pdb
import matplotlib.pyplot as plt
import numpy as np
import warnings

sys.path.append('../')

from plotting_utils import load_glmhmm_data, load_cv_arr, load_data, \
    get_file_name_for_best_model_fold, partition_data_by_session, \
    create_violation_mask, get_marginal_posterior

if __name__ == '__main__':
    animal_array = ["M1", "M1_CNO", "M1_Sal", "M15"]
    K_list = [2,3,4,5,6]

    for animal in animal_array:
        for K in K_list:

            data_dir = '../../data/data_for_cluster/data_by_animal/'
            results_dir = '../../results/individual_fit/' + animal + '/'
            figure_dir = '../../figures/figure_2' + '_' + animal + '_K' + str(K) + '/'

            accuracies_to_plot = []

            inpt, old_y, session = load_data(data_dir + animal + '_processed.npz')
            unnormalized_inpt, _, _ = load_data(data_dir + animal +
                                                '_unnormalized.npz')
            y = np.copy(old_y)  # use this for calculating accuracy; use old_y for
            # calculating posterior probs

            violation_idx = np.where(y == -1)[0]
            nonviolation_idx, mask = create_violation_mask(violation_idx,
                                                        inpt.shape[0])
            old_y[np.where(old_y == -1), :] = 1
            inputs, datas, masks = partition_data_by_session(
                np.hstack((inpt, np.ones((len(inpt), 1)))), old_y, mask,
                session)
            inpt, y, unnormalized_inpt = inpt[nonviolation_idx, :], \
                                        y[nonviolation_idx, :], unnormalized_inpt[
                                                                nonviolation_idx, :]

            # Get accuracy of animal overall:
            not_zero_loc = np.where(unnormalized_inpt[:, 0] != 0)[0]
            correct_ans = (np.sign(unnormalized_inpt[not_zero_loc, 0]) + 1) / 2
            acc = np.sum(y[not_zero_loc, 0] == correct_ans) / len(correct_ans)
            accuracies_to_plot.append(acc)

            # get accuracies in each of the three states:
            cv_file = results_dir + "/cvbt_folds_model.npz"
            cvbt_folds_model = load_cv_arr(cv_file)

            with open(results_dir + "/best_init_cvbt_dict.json", 'r') as f:
                best_init_cvbt_dict = json.load(f)

            # Get the file name corresponding to the best initialization for given K
            # value
            raw_file = get_file_name_for_best_model_fold(cvbt_folds_model, K,
                                                        results_dir,
                                                        best_init_cvbt_dict)
            hmm_params, lls = load_glmhmm_data(raw_file)
            weight_vectors = hmm_params[2]
            posterior_probs = get_marginal_posterior(inputs, datas, masks, hmm_params,
                                                    K, range(K))
            states_max_posterior = np.argmax(posterior_probs, axis=1)

            for k in range(K):
                ## np.where((posterior_probs[:, k] >= 0.9) & (mask == 1))[0]
                idx_of_interest = \
                    np.where((posterior_probs[:, k] >= 0.5) & (mask == 1))[0]
                inpt_this_state, unnormalized_inpt_this_state, y_this_state = \
                    inpt[idx_of_interest, :], unnormalized_inpt[idx_of_interest, :], \
                    y[idx_of_interest, :]
                not_zero_loc = np.where(unnormalized_inpt_this_state[:, 0] != 0)[0]
                correct_ans = (np.sign(unnormalized_inpt_this_state[not_zero_loc, 0]) +
                            1) / 2
                # pdb.set_trace()
                # try:
                    # with warnings.catch_warnings():
                    #     warnings.simplefilter("error", RuntimeWarning)  # Treat RuntimeWarnings as exceptions
                acc = np.sum(y_this_state[not_zero_loc,
                                            0] == correct_ans) / len(correct_ans)
                        
                # except RuntimeWarning:
                #     acc = 0
                #     # pdb.set_trace()
                accuracies_to_plot.append(acc)
                # acc = 0
            # pdb.set_trace()
            cols = [
                '#ff7f00', '#4daf4a', '#377eb8', '#f781bf', '#a65628', '#984ea3',
                '#999999', '#e41a1c', '#dede00'
            ]

            fig = plt.figure(figsize=(1.3, 1.7))
            plt.subplots_adjust(left=0.4, bottom=0.3, right=0.95, top=0.95)
            for z, acc in enumerate(accuracies_to_plot):
                if z == 0:
                    col = 'grey'
                else:
                    col = cols[z - 1]
                plt.bar(z, acc*100, width=0.8, color=col)
            plt.ylim((0, 100))
            # plt.xticks([0, 1, 2, 3, 4], ['All', '1', '2', '3', '4'], fontsize=10)
            # pdb.set_trace()
            xticks_ = np.concatenate((np.array([0]),np.array(range(1,K+1))))
            plt.xticks(xticks_,
                    ('All', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')[:(K+1)])
            # plt.xticks([0, 1, 2], ['All', '1', '2'], fontsize=10)
            plt.yticks([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], fontsize=8)
            plt.xlabel('state', fontsize=10)
            plt.ylabel('accuracy (%)', fontsize=10, labelpad=-0.5)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            fig.savefig(figure_dir + 'fig2f.pdf')
            plt.close()