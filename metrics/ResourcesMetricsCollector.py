import asyncio
import subprocess

from utils.KubernetesClient import KubernetesClient, PodsNotReadyError, \
    NoPodsError
from config import CONFIG


class ResourcesMetricsCollector:
    def __init__(self):
        pass

    def get_metrics(self):
        print(
            'Deleting existing deployment and waiting for pods to terminate...')
        self._delete_deployment()
        self._collect_pods_startup()
        print('[OK] No pods exists in namespace')

        print('Applying deployment...')
        self._apply_deployment()
        print('[OK] Deployment applied')

        print('Collecting pod list...')
        pods = self._collect_pods()
        print('[OK] Pods list collected')

        metrics = dict()

        for pod in pods:
            metrics[pod] = []

        print('Collecting initial metrics...')
        initial_metrics = self._collect_initial_metrics(pods)
        metrics = self._append_metrics(metrics, initial_metrics)
        print('[OK] Initial metrics collected')

        print('Starting running tests...')
        for pod in pods:
            command = 'kubectl exec -it ' + pod + ' -- ' \
                      + CONFIG['tests_command']

            pod_metrics = asyncio \
                .get_event_loop() \
                .run_until_complete(self._run_tests(command, pod))

            metrics = self._append_metrics(metrics, pod_metrics)

            # Metrics can show up with a delay
            for i in range(1, 5):
                asyncio.get_event_loop().run_until_complete(
                    asyncio.sleep(CONFIG['tests_metrics_scrape_interval']))

                delayed_metrics = KubernetesClient.collect_metrics([pod])
                metrics = self._append_metrics(metrics, delayed_metrics)

            print('[OK] Tests finished for pod ' + pod)

        print('[OK] All tests finished')

        print('Collecting final metrics...')
        final_metrics = KubernetesClient.collect_metrics(pods)
        metrics = self._append_metrics(metrics, final_metrics)
        print('[OK] Final metrics collected')

        print('Removing deployment...')
        self._delete_deployment()
        print('[OK] Deployment removed')

        return metrics

    async def _run_tests(self, command, pod):
        metrics = []
        output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        while output is not None:
            retcode = output.poll()
            if retcode is not None:
                return metrics
            else:
                current_metrics = KubernetesClient.collect_metrics([pod])
                if current_metrics is not None and len(current_metrics) == 1:
                    metrics.append(
                        (current_metrics[0][0], current_metrics[0][1]))
                await asyncio.sleep(CONFIG['tests_metrics_scrape_interval'])

    def _collect_pods_startup(self):
        pods_init = None
        i = 0
        while (pods_init is None or len(pods_init) > 0) \
                and i < CONFIG['startup_pod_terminate_timeout']:
            i += 1
            try:
                pods_init = KubernetesClient.collect_pods()
            except PodsNotReadyError:
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))
            except NoPodsError:
                pods_init = []

        if pods_init is None or len(pods_init) != 0:
            raise RuntimeError(
                'There are existing pods that wasn\'t terminated in time.')

    def _collect_pods(self):
        pods = None
        i = 0
        while pods is None and i < CONFIG['pod_creation_timeout']:
            i += 1
            try:
                pods = KubernetesClient.collect_pods()
            except RuntimeError:
                asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))

        if pods is None:
            raise RuntimeError('Pods list cannot be collected.')

        return pods

    def _delete_deployment(self):
        KubernetesClient.delete_deployment(CONFIG['bash_path'],
                                           CONFIG['deployment_path'])

    def _apply_deployment(self):
        KubernetesClient.apply_deployment(CONFIG['bash_path'],
                                          CONFIG['deployment_path'])

    def _collect_initial_metrics(self, pods):
        initial_metrics = None
        i = 0
        while (initial_metrics is None or len(initial_metrics) != len(pods)) \
                and i < CONFIG['startup_pod_terminate_timeout']:
            i += 1
            initial_metrics = KubernetesClient.collect_metrics(pods)
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))

        if initial_metrics is None:
            raise RuntimeError('Metrics does not started up in time.')

        return initial_metrics

    def _append_metrics(self, metrics_dict, collected):
        for pod, data in collected:
            metrics_dict[pod].append(data)

        return metrics_dict
