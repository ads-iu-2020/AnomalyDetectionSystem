import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor

from storage import DataStorage

np.random.seed(42)

storage = DataStorage()

records = pd.read_csv(storage.dataset_file_name)
X = records[['average_cpu', 'average_memory']]
y = records['is_normal']

clf = LocalOutlierFactor(n_neighbors=5, contamination=0.1)

y_pred = clf.fit_predict(X)
X_scores = clf.negative_outlier_factor_

plt.title("Local Outlier Factor (LOF)")
plt.scatter(X.iloc[:, 0].values, X.iloc[:, 1].values, color='k', s=3.,
            label='Data points')
radius = (X_scores.max() - X_scores) / (X_scores.max() - X_scores.min())
plt.scatter(X.iloc[:, 0].values, X.iloc[:, 1].values, s=1000 * radius,
            edgecolors='r',
            facecolors='none', label='Outlier scores')

plt.ylabel('Average memory usage')
plt.xlabel('Average CPU usage')

legend = plt.legend(loc='upper left')
legend.legendHandles[0]._sizes = [10]
legend.legendHandles[1]._sizes = [20]

plt.show()
