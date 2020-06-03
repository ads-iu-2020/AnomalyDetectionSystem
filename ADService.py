from ADModel import ADModel
from metrics.MetricsCollector import MetricsCollector
from storage import DataStorage


class ADService:
    def __init__(self):
        self.metricsCollector = MetricsCollector()
        self.dataStorage = DataStorage()
        self.model = ADModel(self.dataStorage.fields,
                             self.dataStorage.is_normal_field,
                             self.dataStorage.get_records())

    def analyze(self, git_commit, git_pull_request):
        metrics_response = self.metricsCollector.get_metrics(git_pull_request)
        self.dataStorage.add_to_pending(git_commit, **vars(metrics_response))

        print('[OK] Metrics saved')

        is_normal = self.model.predict(**vars(metrics_response))

        if not is_normal:
            raise RuntimeError('[ERROR] Anomaly behaviour is detected!')

        print('[OK] Release is normal, no anomaly behaviour detected.')

    def set_commit_as_merged(self, commit, pull_request_id, merged_at):
        self.dataStorage.set_commit_as_merged(commit, pull_request_id,
                                              merged_at)

    def set_pull_request_as_abnormal(self, pull_request_id):
        self.dataStorage.set_pull_request_as_abnormal(pull_request_id)
