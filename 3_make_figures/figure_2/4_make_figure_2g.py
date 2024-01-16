# Plot figure 2g of Ashwood et al. (2020)
import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import pdb
sys.path.append('../')

from plotting_utils import load_glmhmm_data, load_cv_arr, load_data, \
    get_file_name_for_best_model_fold, \
    partition_data_by_session, create_violation_mask, \
    get_marginal_posterior, get_prob_right


if __name__ == '__main__':
    animal_array = ["M1", "M1_CNO", "M1_Sal", "M15"]
    K_list = [2,3,4, 5, 6]

    for animal in animal_array:
        for K in K_list:
            alpha_val = 2
            sigma_val = 2
            
            data_dir = '/Users/cecelia/Desktop/glm-hmm/data/data_for_cluster/data_by_animal/'
            results_dir = '/Users/cecelia/Desktop/glm-hmm/results/individual_fit/' + animal + '/'
            figure_dir = '../../figures/figure_2' + '_' + animal + '_K' + str(K) + '/'

            if K <= 3:
                fig_size = 5
            elif K==4:
                fig_size = 7
            elif K==5:
                fig_size = 10
            elif K>5:
                fig_Size = 12
            fig = plt.figure(figsize=(fig_size, 2), dpi=80, facecolor='w', edgecolor='k')
            plt.subplots_adjust(left=0.13, bottom=0.23, right=0.9, top=0.8, wspace=0.5,hspace=0.4)
            
            inpt, y, session = load_data(data_dir + animal + '_processed.npz')
            unnormalized_inpt, _, _ = load_data \
                (data_dir + animal + '_unnormalized.npz')

            # Create masks for violation trials
            violation_idx = np.where(y == -1)[0]
            nonviolation_idx, mask = create_violation_mask(violation_idx,
                                                        inpt.shape[0])
            y[np.where(y == -1), :] = 1
            inputs, datas, masks = partition_data_by_session(
                np.hstack((inpt, np.ones((len(inpt), 1)))), y, mask, session)

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

            posterior_probs = get_marginal_posterior(inputs, datas, masks,
                                                    hmm_params, K, range(K))
            states_max_posterior = np.argmax(posterior_probs, axis=1)
            cols = [
                '#ff7f00', '#4daf4a', '#377eb8', '#f781bf', '#a65628', '#984ea3',
                '#999999', '#e41a1c', '#dede00'
            ]
            
            for k in range(K):
                plt.subplot(1, K, k+1)
                # if k == 2:
                #     pdb.set_trace()
                # USE GLM WEIGHTS TO GET PROB RIGHT
                stim_vals, prob_right_max = get_prob_right(-weight_vectors, inpt, k, 1,
                                                        1)
                _, prob_right_min = get_prob_right(-weight_vectors, inpt, k, 0, -1)
                plt.plot(stim_vals,
                        prob_right_max,
                        '-',
                        color=cols[k],
                        alpha=1,
                        lw=1,
                        zorder=5)  #  went R and was rewarded on previous trial
                plt.plot(stim_vals,
                        get_prob_right(-weight_vectors, inpt, k, 0, 1)[1],
                        '--',
                        color=cols[k],
                        alpha=0.5,
                        lw=1)  # went L and was not rewarded on previous trial
                plt.plot(stim_vals,
                        get_prob_right(-weight_vectors, inpt, k, 1, -1)[1],
                        '-',
                        color=cols[k],
                        alpha=0.5,
                        lw=1,
                        markersize=3)  # went R and was not rewarded on previous trial
                plt.plot(stim_vals, prob_right_min, '--', color=cols[k], alpha=1,
                        lw=1)  # went L and was rewarded on previous trial
                
                plt.xticks([min(stim_vals), 0, max(stim_vals)],
                        labels=['', '', ''],
                        fontsize=10)
                plt.yticks([0, 0.5, 1], ['', '', ''], fontsize=10)
                plt.ylabel('')
                plt.xlabel('')
                
                plt.title("state " + str(k), fontsize=10, color=cols[k])
                plt.xticks([min(stim_vals), 0, max(stim_vals)],
                        labels=['-100', '0', '100'],
                        fontsize=10)
                plt.yticks([0, 0.5, 1], ['0', '0.5', '1'], fontsize=10)
                plt.ylabel('p("Horizontal")', fontsize=10)
                plt.xlabel('stimulus', fontsize=10)

                plt.axhline(y=0.5, color="k", alpha=0.45, ls=":", linewidth=0.5)
                plt.axvline(x=0, color="k", alpha=0.45, ls=":", linewidth=0.5)
                plt.gca().spines['right'].set_visible(False)
                plt.gca().spines['top'].set_visible(False)
                plt.ylim((-0.01, 1.01))

        #     ax = plt.subplot(1, K+1, K+1)
        #     for k in range(K):
        #         hor_vert_ratio = np.sum(inpt[:,0] == 1)/len(inpt)
        #         pdb.set_trace()
        #         pair = str(k)
        #         ax.barh(pair, hor_vert_ratio, color=cols[k], label='Horz' if k == 0 else "")
        #         ax.barh(pair, 1-hor_vert_ratio, left=hor_vert_ratio, color=cols[k], alpha = 0.5, label='Vert' if k == 0 else "")
        #         plt.xticks([0, 0.5, 1], ['0', '0.5', '1'], fontsize=10)
        #         plt.xlabel('Horizontal vs. Vertical', fontsize=10)
        #         plt.ylabel('State')
            fig.savefig(figure_dir + 'fig2g.pdf')
            plt.close()
