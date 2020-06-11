import torch
import numpy as np
from sklearn import __all__
import sklearn
from sklearn.cluster import KMeans

def someFunc(a, b, c):
    return a + b + c

print("HelloWorld")
sklearn_version = sklearn.__version__
np_version = np.__version__
concat_version = sklearn_version + np_version
print(concat_version)

print(someFunc(1,2,someFunc(2,3,4)))
kmeans = KMeans(n_clusters=2, random_state=0, n_jobs = 4, precompute_distances=True)
KMeans(n_clusters=3) if 3 > 2 else KMeans(n_clusters=1)