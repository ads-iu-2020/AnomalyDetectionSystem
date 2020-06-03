import json
import re

from ADService import ADService


class WebHooksHandler:
    def __init__(self):
        self.service = ADService()

    def handle(self, json_body):
        print(json_body)
        body = json.loads(json_body)
        if body['action'] == 'closed' and 'pull_request' in body:
            self._handle_pull_request_merge(body)
        elif body['action'] == 'opened' and 'issue' in body:
            self._handle_issue(body)

    def _handle_pull_request_merge(self, body):
        commit = body['pull_request']['head']['sha']
        pull_request_id = body['pull_request']['number']
        merged_at = body['pull_request']['merged_at']

        self.service.set_commit_as_merged(commit, pull_request_id, merged_at)

    def _handle_issue(self, body):
        is_bug = False
        for label in body['issue']['labels']:
            if label['name'] == 'bug':
                is_bug = True
                break

        if not is_bug:
            return

        mentions = re.findall(r"#(\d+)", body['issue']['body'])

        if len(mentions) == 0 or len(mentions) > 1:
            return

        pull_request_id = mentions[0]

        self.service.set_pull_request_as_abnormal(pull_request_id)
