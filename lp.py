import numpy as np
from scipy.spatial.distance import cdist
from typing import List
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns


def vns_p_median(distances: np.ndarray, p: int, k_max: int, biomass: np.ndarray) -> List[int]:
    n = distances.shape[0]
    # Step 1: Generate an initial solution
    x = np.zeros(n, dtype=int)
    indices = np.arange(n)
    np.random.shuffle(indices)
    x[indices[:p]] = 1
    k=1
    # Step 2: Local search
    while k < k_max:
        print('k = ' + str(k))
        # Step 2.1: Shake
        x_new = shake(x, k)

        # Step 2.2: Local search
        x_new = local_search_p_median(distances, x_new, p, biomass)

        # Step 2.3: Acceptance criterion
        if objective_function_p_median(distances, x_new, biomass) < objective_function_p_median(distances, x, biomass):
            x = x_new
            k = 1
        else:
            k += 1
        # tqdm update
    # Step 3: Return the best solution found
    return np.where(x == 1)[0].tolist(), objective_function_p_median(distances, x, biomass)

def shake(x: np.ndarray, k: int) -> np.ndarray:  
    x_new = x.copy()
    indices = np.where(x == 1)[0]
    np.random.shuffle(indices)
    
    x_new[indices[:k]] = 0
    x_new[indices[k:]] = 1

    return x_new

def local_search_p_median(distances: np.ndarray, x: np.ndarray, p: int, biomass: np.ndarray) -> np.ndarray:
    n = distances.shape[0]
    l=1
    l_max = 5
    iter=0
    iter_max=500
    while l <= l_max:
        # Step 1: Find the p medians
        medians = np.where(x == 1)[0]
        
        # Step 2: Assign each point to the closest median
        clusters = np.argmin(distances[:, medians], axis=1)
        # Step 3: Compute the new medians   
        for i in range(p):
            if np.sum(clusters == i) > 0:

                # get the distances between the points in the cluster and the other points in the cluster
                cluster_distances = distances[np.logical_or(clusters == i, clusters == i+l), :][:, np.logical_or(clusters == i, clusters == i+l)]
                # get the new median by computing the point that minimizes the sum of the distances to the other points in the cluster
                # the axis =1 because we want the sum of the distances to the other points in the cluster
                # if the axis = 0, we would have the sum of the distances to the other points in the cluster for each point
                new_median = np.argmin(np.sum(cluster_distances, axis=1))
                print(np.sum(cluster_distances, axis=0))
                print(np.sum(cluster_distances, axis=0).shape)
                # get the minimum median that not exists in the medians list
                medians[i]= new_median

            
        # Step 4: Update the solution
        x_new = np.zeros(n, dtype=int)
        x_new[medians] = 1
        if objective_function_p_median(distances, x_new, biomass) < objective_function_p_median(distances, x, biomass):
            x = x_new
            l = 1
        else:
            l += 1
        
        iter += 1
        if iter >= iter_max:
            break
    return x

def objective_function_p_median(distances: np.ndarray, x: np.ndarray, biomass: np.ndarray) -> float:
    medians = np.where(x == 1)[0]
    # pega todas as linhas da matriz de distancias e as colunas correspondentes às medianas
    # assim, temos uma matriz de distancias de cada ponto para cada mediana
    # então, pegamos o índice do eixo 1 (colunas, gerando n_rows elementos) que corresponde à menor distância de cada ponto para cada mediana
    clusters = np.argmin(distances[:, medians], axis=1)
    costs = biomass.reshape(-1, 1) * distances
    obj_func = np.sum(costs[clusters, np.arange(len(clusters))])
    print('Objective function value: ' + str(obj_func))
    return obj_func

distance_matrix = pd.read_csv('dataset/Distance_Matrix.csv').drop('Unnamed: 0', axis=1)
biomass_history = pd.read_csv('dataset/Biomass_History.csv')

# Set the number of medians to be selected
p = 25

# Set the maximum number of iterations for the VNS algorithm
k_max = 10
n = 2417
year = '2010'
distances = distance_matrix.to_numpy()[:n, :n]
biomass = biomass_history[year].to_numpy()[:n]

solution, cost = vns_p_median(distances, p, k_max, biomass)

connections = np.argmin(distances[:, solution], axis=1)

# print solution
print('Solution:')
print(solution)
print('Objective function value:')
print(cost)

# plot solution


sns.set_style('whitegrid')
sns.set_context('paper')
sns.set(font_scale=1.1, font='Cambria')

plt.figure(figsize=(12, 8))
plt.scatter(biomass_history['Longitude'], biomass_history['Latitude'], s=1)
plt.scatter(biomass_history['Longitude'][solution], biomass_history['Latitude'][solution], s=12, c='r')
plt.annotate('p = ' + str(p), xy=(0.05, 0.95), xycoords='axes fraction', fontsize=15)
plt.annotate('k_max = ' + str(k_max), xy=(0.05, 0.9), xycoords='axes fraction', fontsize=15)
plt.annotate('Cost = ' + str(cost), xy=(0.05, 0.85), xycoords='axes fraction', fontsize=15)
# plot the connections
plt.xlabel('x')
plt.ylabel('y')
plt.show()
