import requests

from config import CONFIG


class ProcessMetricsCollector:
    def __init__(self):
        pass

    def get_metrics(self, pull_request_id):
        url = 'https://api.github.com/repos/' + CONFIG[
            'repository_user'] + '/' + CONFIG[
                  'repository_name'] + '/pulls/' + str(pull_request_id)

        headers = {'Accept': 'application/vnd.github.v3.text-match+json',
                   'Authorization': 'token ' + CONFIG['github_token']}

        response = requests.get(url, headers=headers)

        json_response = response.json()

        return json_response['additions'], json_response['deletions'], \
               json_response['changed_files']
