# Produce panels b, c, d and e of Figure 2 of Ashwood et al. (2020)
import json
import os
import sys
import pdb
import numpy as np

sys.path.insert(0, '../')
from plotting_utils import load_glmhmm_data, load_cv_arr, \
    get_file_name_for_best_model_fold

import matplotlib.pyplot as plt

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

            cv_file = results_dir + "/cvbt_folds_model.npz"
            cvbt_folds_model = load_cv_arr(cv_file)

            with open(results_dir + "/best_init_cvbt_dict.json", 'r') as f:
                best_init_cvbt_dict = json.load(f)

            # Get cvbt and pred acc:
            cols = ['#999999', '#984ea3', '#e41a1c', '#dede00']
            cv_arr = load_cv_arr(results_dir + "/cvbt_folds_model.npz")
            # pdb.set_trace()

            # changes made to NOT include the Lapse model value
            # cv_arr_for_plotting = cv_arr[[0, 2, 3, 4, 5, 6, 7], :]
            # pdb.set_trace()
            cv_arr_for_plotting = cv_arr[[0, 3, 4, 5, 6, 7], :] 

            pred_acc_arr = load_cv_arr(results_dir + "predictive_accuracy_mat.npz")
            pred_acc_arr_for_plotting = pred_acc_arr[[0, 3, 4, 5, 6, 7], :]

            # ========== FIG 2b ==========
            fig = plt.figure(figsize=(2, 1.6))
            plt.subplots_adjust(left=0.4, bottom=0.3, right=0.9, top=0.9)
            plt.plot([0, 1, 2, 3, 4, 5],
                    np.mean(cv_arr_for_plotting, axis=1),
                    '-o',
                    color=cols[0],
                    zorder=0,
                    alpha=1,
                    lw=1.5,
                    markersize=4)
            # plt.yticks([0.30, 0.35, 0.4, 0.45],
            #            labels=["0.30", "0.35", "0.40", "0.45"],
            #            fontsize=10)
            plt.xticks([0, 1, 2, 3, 4, 5],
                    labels=['1', '2', '3', '4', '5', '6'],
                    fontsize=10)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.ylabel("test LL (bits/trial)", fontsize=10)
            plt.xlabel("# states", fontsize=10)
            fig.savefig(figure_dir + 'fig2b.pdf')
            plt.close()

            # ========== FIG 2c ==========
            fig = plt.figure(figsize=(2, 1.6))
            plt.subplots_adjust(left=0.3, bottom=0.3, right=0.9, top=0.9)
            plt.plot([0, 1, 2, 3, 4, 5],
                    np.mean(pred_acc_arr_for_plotting, axis=1),
                    '-o',
                    color=cols[1],
                    zorder=0,
                    alpha=1,
                    lw=1.5,
                    markersize=4)
            plt.yticks([0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9],
                    labels=["72", "74", "76", "78", "80", "82", "84", "86", "88", "90"],
                    fontsize=10)
            plt.xticks([0, 1, 2, 3, 4, 5],
                    labels=['1', '2', '3', '4', '5', '6'],
                    fontsize=10)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.ylabel("predictive acc. (%)", fontsize=10)
            plt.xlabel("# states", fontsize=10)
            fig.savefig(figure_dir + 'fig2c.pdf')
            plt.close()

            # =========== Fig 2d =============
            raw_file = get_file_name_for_best_model_fold(cvbt_folds_model, K,
                                                        results_dir,
                                                        best_init_cvbt_dict)
            hmm_params, lls = load_glmhmm_data(raw_file)

            transition_matrix = np.exp(hmm_params[1][0])

            fig = plt.figure(figsize=(1.6, 1.6))
            plt.subplots_adjust(left=0.3, bottom=0.3, right=0.95, top=0.95)
            plt.imshow(transition_matrix, vmin=-0.8, vmax=1, cmap='bone')
            for i in range(transition_matrix.shape[0]):
                for j in range(transition_matrix.shape[1]):
                    text = plt.text(j,
                                    i,
                                    str(np.around(transition_matrix[i, j],
                                                decimals=2)),
                                    ha="center",
                                    va="center",
                                    color="k",
                                    fontsize=8)
            plt.xlim(-0.5, K - 0.5)
            plt.xticks(range(0, K),
                    ('1', '2', '3', '4', '4', '5', '6', '7', '8', '9', '10')[:K],
                    fontsize=10)
            plt.yticks(range(0, K),
                    ('1', '2', '3', '4', '4', '5', '6', '7', '8', '9', '10')[:K],
                    fontsize=10)
            plt.ylim(K - 0.5, -0.5)
            plt.ylabel("state t-1", fontsize=10)
            plt.xlabel("state t", fontsize=10)
            fig.savefig(figure_dir + 'fig2d.pdf')
            plt.close()

            # =========== Fig 2e =============
            weight_vectors = -hmm_params[2]

            cols = [
                '#ff7f00', '#4daf4a', '#377eb8', '#f781bf', '#a65628', '#984ea3',
                '#999999', '#e41a1c', '#dede00'
            ]
            fig = plt.figure(figsize=(2.7, 2.5))
            plt.subplots_adjust(left=0.3, bottom=0.4, right=0.8, top=0.9)
            M = weight_vectors.shape[2] - 1
            for k in range(K):
                # pdb.set_trace()
                plt.plot(range(M + 1),
                        weight_vectors[k][0][:],
                        marker='o',
                        markersize = 2,
                        label="state " + str(k + 1),
                        color=cols[k],
                        lw=1,
                        alpha=0.7)
                
            plt.legend(fontsize=4)
            plt.yticks([-2.5, 0, 2.5, 5], fontsize=10)
            labels_for_plot = [ 'Stim', 'flanker_ori',\
                            'flanker_cont', 'prevStim',\
                            'prevChoice', \
                            'WSLS', 'Bias']
            plt.xticks(
                list(range(0, len(labels_for_plot))),
                labels_for_plot,
                fontsize=8,
                rotation=90)
            plt.ylabel("GLM weight", fontsize=10)
            plt.axhline(y=0, color="k", alpha=0.5, ls="--", lw=0.5)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            fig.savefig(figure_dir + 'fig2e.pdf')
            plt.close()
