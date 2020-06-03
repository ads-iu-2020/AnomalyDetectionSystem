# Anomaly Detection System

Anomaly Detection System created during «Anomaly Detection in Microservices» study.

## Requirements
Python version should be equal to or higher than 3.7.6. The libraries, listed in file `requirements.txt` are required to launch the system.

## System setup
1. Install all requirements
2. Copy `config.py.example` into `config.py`. Update file by entering correct values, using examples in file and parameters described below.
3. Make sure, that Kubernetes API is available using `api_base_url` from the configuration.
4. Launch web server, by running built-in server.py or use another preferred web server
5. Set up the GitHub webhooks. Go into analyzed project repository, open _Settings_, _Webhooks_. In the _Payload URL_ field enter webserver full URL. Content type should be `application/x-www-form-urlencoded`. Only _Pull requests_ and _Issues_ events should be received by webhook. 

If the dataset file has been cleared, make sure, that the records below are inserted so that model can properly analyze first releases.
`,,0.0,0,0.0,0,0,0,0,0,1970-01-01T00:00:00Z,0
,,0.0,0,0.0,0,0,0,0,0,1970-01-01T00:00:00Z,1 `


### Configuration parameters
* `bash_path`: Path to run bash
* `deployment_path`: Full path to Kubernetes deployment
* `api_base_url`: Base url of Kubernetes API
* `namespace`: Kubernetes pods namespace
* `pod_creation_timeout`: Timeout for pods to create before AD System will fail
* `startup_pod_terminate_timeout`: Timeout for existing pods to terminate before AD system will fail
* `tests_metrics_scrape_interval`: Interval between metrics scrapping
* `server_port`: Port to run local server to receive GitHub webhooks
* `tests_command`: Test command to run on pods during executing anomaly detection system
* `github_token`: GitHub token to fetch repository information
* `repository_user`: Owner of analyzed project GitHub repository. Can be a username or name of an organization
* `repository_name`: Analyzed project GitHub repository name
* `dataset_file_path`: Dataset file name to store metrics from accepted releases 
* `augmented_dataset_file_path`: Augmented dataset file name. Used for evaluation, can be omitted
* `pending_file_path`: Dataset file name to store metrics from pending releases

### Use cases
#### Analyze the current release
Launch the Anomaly Detection system for the release by running 
`python __main__.py ${ghprbActualCommit} ${ghprbPullId}`

* `${ghprbActualCommit}` should be replaced with last commit number
* `${ghprbPullId}` should be replaced with GitHub pull request number

For example: `__main__.py ad809065f54b6c93757ca8ac4c436f5b21fa8f00 15`

The [GitHub Pull Request Builder](https://plugins.jenkins.io/ghprb/) plugin for Jenkins can provide the described functionality.

#### Make previous release as anomaly
The issue mentioning only anomaly release should be created in the GitHub repository. The label "Bug" should be attached to the issue before it's creation.


## Evaluation
To plot outliers score for initial and extended datasets, run `lof_plot.py` and `lof_augmented_plot.py` from `evaluation` package, respectively.

To find values for the contingency table, run `evaluation.py` from the `evaluation` package.
