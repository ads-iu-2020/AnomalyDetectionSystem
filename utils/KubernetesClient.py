import subprocess
from json import JSONDecodeError
from config import CONFIG

import requests


class NoPodsError(RuntimeError):
    pass


class PodsNotReadyError(RuntimeError):
    pass


class KubernetesClient:
    @staticmethod
    def collect_metrics(pods):
        response = requests.get(
            CONFIG['api_base_url'] + 'apis/metrics.k8s.io/v1beta1/pods')
        try:
            podMetricList = response.json()
        except JSONDecodeError:
            return None

        return [(a['metadata']['name'], a['containers'][0]['usage'])
                for a in podMetricList['items']
                if a['metadata']['name'] in pods]

    @staticmethod
    def collect_pods():
        pod_list = requests.get(
            CONFIG['api_base_url'] + 'api/v1/namespaces/default/pods').json()
        pods = [a['metadata']['name'] for a in pod_list['items']]

        if len(pods) == 0:
            raise NoPodsError()

        for pod in pod_list['items']:
            if pod['status']['phase'] != 'Running':
                raise PodsNotReadyError()

        return pods

    @staticmethod
    def apply_deployment(bash_path, deployment_path):
        subprocess.run(
            [bash_path, '-c', 'kubectl apply -f ' + deployment_path],
            capture_output=True)

    @staticmethod
    def delete_deployment(bash_path, deployment_path):
        subprocess.run(
            [bash_path, '-c', 'kubectl delete -f ' + deployment_path],
            capture_output=True)
