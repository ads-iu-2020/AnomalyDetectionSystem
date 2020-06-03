import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import SVC

from storage import DataStorage

np.random.seed(42)

storage = DataStorage()

datasets = [
    storage.dataset_file_name,
    storage.augmented_dataset_file_name
]

for dataset in datasets:
    print('Processing dataset: ' + dataset)
    records = pd.read_csv(dataset)
    X = records[storage.fields]
    y = records['is_normal']

    X = X.reset_index(drop=True)
    y = y.reset_index(drop=True)

    lof_tp = 0
    lof_fp = 0
    lof_fn = 0
    lof_tn = 0

    svc_tp = 0
    svc_fp = 0
    svc_fn = 0
    svc_tn = 0

    for i in range(len(X)):
        X_current = X.loc[i]
        X_filtered = X.drop(X.index[[i]])

        y_current = y.loc[i]
        y_filtered = y.drop(y.index[[i]])

        # Process LOF
        lof = LocalOutlierFactor(n_neighbors=5, contamination=0.1)
        lof_y_pred = lof.fit_predict(X)[i]

        if lof_y_pred == -1:
            lof_y_pred = 0

        if lof_y_pred == 1 and y_current == 1:
            lof_tp += 1
        elif lof_y_pred == 1 and y_current == 0:
            lof_fp += 1
        elif lof_y_pred == 0 and y_current == 1:
            lof_fn += 1
        else:
            lof_tn += 1

        svc = SVC()
        svc.fit(X_filtered, y_filtered)
        svc_y_pred = svc.predict([X_current])

        if svc_y_pred == 1 and y_current == 1:
            svc_tp += 1
        elif svc_y_pred == 1 and y_current == 0:
            svc_fp += 1
        elif svc_y_pred == 0 and y_current == 1:
            svc_fn += 1
        else:
            svc_tn += 1

    lof_precision = lof_tp / (lof_tp + lof_fp)
    lof_recall = lof_tp / (lof_tp + lof_fn)

    print("True positives for LOF: " + str(lof_tp))
    print("False positives for LOF: " + str(lof_fp))
    print("False negatives for LOF: " + str(lof_fn))
    print("True negatives for LOF: " + str(lof_tn))
    print("LOF precision: %.2f" % lof_precision)
    print("LOF recall: %.2f" % lof_recall)
    print()

    svc_precision = svc_tp / (svc_tp + svc_fp)
    svc_recall = svc_tp / (svc_tp + svc_fn)

    print("True positives for SVC: " + str(svc_tp))
    print("False positives for SVC: " + str(svc_fp))
    print("False negatives for SVC: " + str(svc_fn))
    print("True negatives for SVC: " + str(svc_tn))
    print("SVC precision: %.2f" % svc_precision)
    print("SVC recall: %.2f" % svc_recall)

    print("\n")
