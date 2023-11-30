import os
import time

from pprint import pprint

from netunicorn.client.remote import RemoteClient, RemoteClientException
from netunicorn.base.experiment import Experiment, ExperimentStatus
from netunicorn.base.pipeline import Pipeline
from netunicorn.library.tasks.measurements.ping import Ping
from netunicorn.library.tasks.basic import ShellCommand
from returns.pipeline import is_successful


pipeline = Pipeline()

pipeline = pipeline.then([
    ShellCommand("ping -D 1.1.1.1 -c 10"),
]).then(
    ShellCommand("sudo apt-get install -y traceroute && traceroute 1.1.1.1")
).then(
    ShellCommand("sudo apt-get install -y curl && curl ipconfig.io")
)

if '.env' in os.listdir():
    from dotenv import load_dotenv
    load_dotenv(".env")

endpoint = os.environ.get('NETUNICORN_ENDPOINT') or 'http://localhost:26611'
login = os.environ.get('NETUNICORN_LOGIN') or 'test'
password = os.environ.get('NETUNICORN_PASSWORD') or 'test'
client = RemoteClient(endpoint=endpoint, login=login, password=password)
client.healthcheck()

nodes = client.get_nodes()

working_nodes = nodes.take(1)
print("Working nodes:", working_nodes)
for node in working_nodes:
    print("name: {}, properties: {}, architecture: {}".format(node.name, node.properties, node.architecture))
print("\n")

experiment = Experiment().map(pipeline, working_nodes)

print("Experiment:", experiment)

for deployment in experiment:
    print("deployment node:", deployment.node)
    print("deployment environment definition:", deployment.environment_definition)
    print("\n")

experiment_name = 'experiment_ping'
try:
    client.delete_experiment(experiment_name)
except RemoteClientException as e:
    pass

client.prepare_experiment(experiment, experiment_name)


while True:
    info = client.get_experiment_status(experiment_name)
    print(info.status)
    if info.status == ExperimentStatus.READY:
        break
    time.sleep(10)


while True:
    info = client.get_experiment_status(experiment_name)
    print(info.status)
    if info.status == ExperimentStatus.READY:
        break
    time.sleep(20)

prepared_experiment = info.experiment
for deployment in prepared_experiment:
    print(f"Node name: {deployment.node}")
    print(f"Deployed correctly: {deployment.prepared}")
    print(f"Error: {deployment.error}")


client.start_execution(experiment_name)


while True:
    info = client.get_experiment_status(experiment_name)
    print(info.status)
    if info.status != ExperimentStatus.RUNNING:
        break
    time.sleep(10)


for report in info.execution_result:
    print(f"Node name: {report.node.name}")
    print(f"Error: {report.error}")

    result, log = report.result
    if not is_successful(result):
        print("failed: ", result)