# Create panels a-c of Figure 3 of Ashwood et al. (2020)
import json
import os
import sys
import pdb
import matplotlib.pyplot as plt
import numpy as np

sys.path.append('../')

from plotting_utils import load_glmhmm_data, load_cv_arr, load_data, \
    get_file_name_for_best_model_fold, partition_data_by_session, \
    create_violation_mask, get_marginal_posterior, get_was_correct


if __name__ == '__main__':
    animal_array = ["M1", "M1_CNO", "M1_Sal", "M15"]
    K_list = [2,3,4, 5, 6]
    for animal in animal_array:
        for K in K_list:
            data_dir = '/Users/cecelia/Desktop/glm-hmm/data/data_for_cluster/data_by_animal/'
            results_dir = '/Users/cecelia/Desktop/glm-hmm/results/individual_fit/' + animal + '/'
            figure_dir = '../../figures/figure_2' + '_' + animal + '_K' + str(K) + '/'

            if not os.path.exists(figure_dir):
                os.makedirs(figure_dir)

            np.random.seed(59)

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

            # Save parameters for initializing individual fits
            weight_vectors = hmm_params[2]
            log_transition_matrix = hmm_params[1][0]
            init_state_dist = hmm_params[0][0]

            # Also get data for animal:
            inpt, y, session = load_data(data_dir + animal + '_processed.npz')
            all_sessions = np.unique(session)
            # Create mask:
            # Identify violations for exclusion:
            violation_idx = np.where(y == -1)[0]
            nonviolation_idx, mask = create_violation_mask(violation_idx,
                                                        inpt.shape[0])
            y[np.where(y == -1), :] = 1
            inputs, datas, train_masks = partition_data_by_session(
                np.hstack((inpt, np.ones((len(inpt), 1)))), y, mask,
                session)

            posterior_probs = get_marginal_posterior(inputs, datas, train_masks,
                                                    hmm_params, K, range(K))
            states_max_posterior = np.argmax(posterior_probs, axis=1)
            # pdb.set_trace()
            sess_to_plot = all_sessions
            # ["M1-session1", "M1-session2",  "M1-session3", \
            #                 "M1-session4", "M1-session5", "M1-session6"]

            cols = ['#ff7f00', '#4daf4a', '#377eb8', '#f781bf', '#a65628', '#984ea3',
                    '#999999', '#e41a1c', '#dede00']
            
            if len(sess_to_plot) <= 8:
                length_ = 3
                width_ = 3
                fig = plt.figure(figsize=(6, 5))
                plt.subplots_adjust(wspace=0.2, hspace=0.9)
            else:
                length_ = 5
                width_ = 3
                fig = plt.figure(figsize=(6, 9))
                plt.subplots_adjust(wspace=0.2, hspace=0.9)

            # fig = plt.figure(figsize=(6, 5))
            # plt.subplots_adjust(wspace=0.2, hspace=0.9)
            for i, sess in enumerate(sess_to_plot):
                plt.subplot(length_, width_, i + 1)
                idx_session = np.where(session == sess)
                this_inpt, this_y = inpt[idx_session[0], :], y[idx_session[0], :]
                was_correct, idx_easy = get_was_correct(this_inpt, this_y)
                this_y = this_y[:, 0] + np.random.normal(0, 0.03, len(this_y[:, 0]))
                # plot choice, color by correct/incorrect:
                locs_correct = np.where(was_correct == 1)[0]
                locs_incorrect = np.where(was_correct == 0)[0]
                plt.plot(locs_correct, this_y[locs_correct], 'o', color='black',
                        markersize=2, zorder=3, alpha=0.5)
                plt.plot(locs_incorrect, this_y[locs_incorrect], 'v', color='red',
                        markersize=2, zorder=4, alpha=0.5)

                states_this_sess = states_max_posterior[idx_session[0]]
                state_change_locs = np.where(np.abs(np.diff(states_this_sess)) > 0)[0]
                for change_loc in state_change_locs:
                    plt.axvline(x=change_loc, color='k', lw=0.1,alpha=0.5, linestyle='--')
                plt.ylim((-0.13, 1.13))
                if i == 0:
                    plt.xticks([0, 45, 90], ["0", "45", "90"], fontsize=10)
                    plt.yticks([0, 1], ["L", "R"], fontsize=10)
                else:
                    plt.xticks([0, 45, 90], ["", "", ""], fontsize=10)
                    plt.yticks([0, 1], ["", ""], fontsize=10)
                plt.gca().spines['right'].set_visible(False)
                plt.gca().spines['top'].set_visible(False)
                plt.title("example session " + str(i + 1), fontsize=10)
                if i == 0:
                    plt.xlabel("trial #", fontsize=10)
                    plt.ylabel("choice", fontsize=10)
            fig.savefig(figure_dir + 'fig3abc_choice.pdf')
            plt.close()

            fig = plt.figure(figsize=(6, 5))
            if len(sess_to_plot) <= 8:
                length_ = 3
                width_ = 3
                fig = plt.figure(figsize=(6, 5))
                plt.subplots_adjust(wspace=0.2, hspace=0.9)
            else:
                length_ = 5
                width_ = 3
                fig = plt.figure(figsize=(6, 9))
                plt.subplots_adjust(wspace=0.2, hspace=0.9)
            for i, sess in enumerate(sess_to_plot):
                plt.subplot(length_, width_, i + 1)
                idx_session = np.where(session == sess)
                this_inpt = inpt[idx_session[0], :]
                posterior_probs_this_session = posterior_probs[idx_session[0], :]
                # Plot trial structure for this session too:
                # pdb.set_trace()
                for k in range(K):
                    plt.plot(posterior_probs_this_session[:, k],
                            label="State " + str(k + 1), lw=1,
                            color=cols[k])
                states_this_sess = states_max_posterior[idx_session[0]]
                state_change_locs = np.where(np.abs(np.diff(states_this_sess)) > 0)[0]
                for change_loc in state_change_locs:
                    plt.axvline(x=change_loc, color='k', lw=0.1,alpha=0.5, linestyle='--')
                if i == 0:
                    plt.xticks([0, 45, 90], ["0", "45", "90"], fontsize=10)
                    plt.yticks([0, 0.5, 1], ["0", "0.5", "1"], fontsize=10)
                else:
                    plt.xticks([0, 45, 90], ["", "", ""], fontsize=10)
                    plt.yticks([0, 0.5, 1], ["", "", ""], fontsize=10)
                plt.ylim((-0.01, 1.01))
                plt.title("example session " + str(i + 1), fontsize=10)
                plt.gca().spines['right'].set_visible(False)
                plt.gca().spines['top'].set_visible(False)
                if i == 0:
                    plt.xlabel("trial #", fontsize=10)
                    plt.ylabel("p(state)", fontsize=10)

            # Now plot avg session:
            posterior_probs_mat = []
            max_session_len = 0
            for i, sess in enumerate(all_sessions):
                idx_session = np.where(session == sess)
                posterior_probs_this_session = posterior_probs[idx_session[0], :]
                # if len(posterior_probs_this_session) == 90:
                this_len = len(posterior_probs_this_session)
                if this_len > max_session_len:
                    max_session_len = this_len
            
            for i, sess in enumerate(all_sessions):
                idx_session = np.where(session == sess)
                posterior_probs_this_session = posterior_probs[idx_session[0], :]
                padding = ((0, max_session_len - len(posterior_probs_this_session)),\
                    (0,0))
                posterior_probs_this_session = np.pad(\
                    posterior_probs_this_session, \
                    pad_width = padding, mode='constant', constant_values=np.nan)
                posterior_probs_mat.append(posterior_probs_this_session)
            
            posterior_probs_mat = np.array(posterior_probs_mat)
            avg_posterior = np.mean(posterior_probs_mat, axis=0)
            std_dev_posterior = np.std(posterior_probs_mat, axis=0)
            
            plt.subplot(length_, width_, i + 2)
            for k in range(K):
                plt.plot(avg_posterior[:, k], label="State " + str(k + 1), lw=1,
                        color=cols[k])
                se = std_dev_posterior[:, k] / np.sqrt(posterior_probs_mat.shape[0])
                plt.plot(avg_posterior[:, k] + se, color=cols[k], alpha=0.2)
                plt.plot(avg_posterior[:, k] - se, color=cols[k], alpha=0.2)

            plt.xticks([0, 45, 90], ["", "", ""], fontsize=10)
            plt.yticks([0, 0.5, 1], ["", "", ""], fontsize=10)
            plt.ylim((-0.01, 1.01))
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.title("avg. session ", fontsize=10)
            plt.xlabel("trial #", fontsize=10)
            plt.ylabel("p(state)", fontsize=10)
            plt.xticks([0, 45, 90], ["0", "45", "90"], fontsize=10)
            plt.yticks([0, 0.5, 1], ["0", "0.5", "1"], fontsize=10)
            fig.savefig(figure_dir + 'fig3abc_pstate.pdf')
            plt.close()
