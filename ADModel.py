from sklearn import svm


class ADModel:
    def __init__(self, fields, is_normal_field, records):
        self.fields = fields
        self.is_normal_field = is_normal_field
        self.records = records

        self.clf = svm.SVC()

    def predict(self, **metrics):
        X = self.records[self.fields]
        y = self.records[self.is_normal_field]

        if X.shape[0] == 0 or y.shape[0] == 0:
            return 1

        clf = svm.SVC()
        clf.fit(X, y)

        vals = [list(metrics.values())]
        prediction = clf.predict(vals)

        return prediction[0]
