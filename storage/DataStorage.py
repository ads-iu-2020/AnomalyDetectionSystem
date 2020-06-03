import time
from datetime import datetime, timedelta
import os

import pytz

from config import CONFIG
import pandas as pd
import janitor  # After import becomes part of pandas


class DataStorage:
    def __init__(self):
        self.dataset_file_name = CONFIG['dataset_file_path']
        self.augmented_dataset_file_name = CONFIG[
            'augmented_dataset_file_path']
        self.pending_file_name = CONFIG['pending_file_path']

        self.commit_field = 'commit'
        self.pull_request_field = 'pull_request'
        self.merged_at_field = 'merged_at'
        self.is_normal_field = 'is_normal'

        self.fields = [
            'average_cpu', 'max_cpu', 'average_memory',
            'max_memory', 'lines_added', 'lines_deleted',
            'changed_files'
        ]

        self.pending_columns = [self.commit_field] + self.fields

        self.dataset_columns = [self.commit_field] + self.fields \
                               + [self.pull_request_field,
                                  self.merged_at_field, self.is_normal_field]

    def get_records(self):
        if not os.path.isfile(self.dataset_file_name):
            return pd.DataFrame(columns=self.dataset_columns)

        metrics_consider_from = datetime.fromtimestamp(0, tz=pytz.UTC)
        metrics_consider_to = datetime.now(tz=pytz.UTC) - timedelta(days=7)
        # metrics_consider_to = datetime.now(tz=pytz.UTC)

        records = pd.read_csv(self.dataset_file_name)
        records = records.filter_date('merged_at', metrics_consider_from,
                                      metrics_consider_to)

        return records

    def add_to_pending(self, git_commit, **metrics):
        metrics[self.commit_field] = git_commit

        df = pd.DataFrame(columns=self.pending_columns)
        df = df.append(metrics, ignore_index=True)

        df.to_csv(self.pending_file_name, mode='a+',
                  header=(not os.path.exists(self.pending_file_name)))

    def set_commit_as_merged(self, git_commit, pull_request_id, merged_at):
        pending_df = pd.read_csv(self.pending_file_name, index_col=[0])

        commit_data = pending_df.loc[
            pending_df[self.commit_field] == git_commit]
        commit_data[self.pull_request_field] = pull_request_id
        commit_data[self.merged_at_field] = merged_at
        commit_data[self.is_normal_field] = 1

        commit_data.to_csv(self.dataset_file_name, mode='a+',
                           header=(not os.path.exists(self.dataset_file_name)))

        pending_df_drop = pending_df.drop(pending_df.query(
            self.commit_field + '=="' + git_commit + '"').index)
        pending_df_drop.to_csv(self.pending_file_name, index=False)

    def set_pull_request_as_abnormal(self, pull_request_id):
        df = pd.read_csv(self.dataset_file_name, index_col=[0])
        df.loc[df[self.pull_request_field] == int(
            pull_request_id), self.is_normal_field] = 0
        df.to_csv(self.dataset_file_name, index=False)
