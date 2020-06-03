import re

from metrics import ProcessMetricsCollector, ResourcesMetricsCollector, \
    MetricsResponse


class MetricsCollector:
    def __init__(self):
        self.resourcesCollector = ResourcesMetricsCollector()
        self.processCollector = ProcessMetricsCollector()

    def get_metrics(self, pull_request_id) -> MetricsResponse:
        print('Starting metrics collection...')

        print('Starting resources metrics collection...')
        resources_metrics = self.resourcesCollector.get_metrics()
        average_cpu, max_cpu, average_memory, max_memory = \
            self._handle_resources_metrics(resources_metrics)
        print('[OK] Resources metrics collected...')

        print('Starting process metrics collection...')
        lines_added, lines_deleted, changed_files = \
            self.processCollector.get_metrics(pull_request_id)
        print('[OK] Process metrics collected...')

        print('[OK] All metrics successfully fetched')

        response = MetricsResponse(average_cpu=average_cpu,
                                   max_cpu=max_cpu,
                                   average_memory=average_memory,
                                   max_memory=max_memory,
                                   lines_added=lines_added,
                                   lines_deleted=lines_deleted,
                                   changed_files=changed_files)

        return response

    def _handle_resources_metrics(self, pod_metrics):
        cpu_records = []
        memory_records = []

        for pod, metrics in pod_metrics.items():
            for metric in metrics:
                cpu_records.append(
                    int(re.search('[0-9]+', metric['cpu']).group()))
                memory_records.append(
                    int(re.search('[0-9]+', metric['memory']).group()))

        average_cpu = sum(cpu_records) / len(cpu_records)
        max_cpu = max(cpu_records)
        average_memory = sum(memory_records) / len(memory_records)
        max_memory = max(memory_records)

        return average_cpu, max_cpu, average_memory, max_memory
