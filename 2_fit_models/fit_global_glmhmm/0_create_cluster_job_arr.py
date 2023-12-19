#  In order to facilitate parallelization of jobs, create a job array that
#  can be used on e.g. a cluster
import numpy as np
# import pdb
K_vals = [2,3,4,5,6,7]#[2, 3, 4] #num of hidden states
num_folds = 3
N_initializations = 5

if __name__ == '__main__':
    cluster_job_arr = []
    for K in K_vals:
        for i in range(num_folds):
            for j in range(N_initializations):
                cluster_job_arr.append([K, i, j])
    # pdb.set_trace()
    np.savez('/Users/cecelia/Desktop/glm-hmm/data/data_for_cluster/cluster_job_arr.npz',
             cluster_job_arr)
