import time
import os
from pprint import pprint
from netunicorn.client.remote import RemoteClient, RemoteClientException
from netunicorn.base.experiment import Experiment, ExperimentStatus
from netunicorn.base.pipeline import Pipeline
from netunicorn.library.tasks.measurements.ping import Ping
from returns.pipeline import is_successful

if '.env' in os.listdir():
    from dotenv import load_dotenv
    load_dotenv(".env")

endpoint = os.environ.get('NETUNICORN_ENDPOINT') or 'http://localhost:26611'
login = os.environ.get('NETUNICORN_LOGIN') or 'test'
password = os.environ.get('NETUNICORN_PASSWORD') or 'test'

client = RemoteClient(endpoint=endpoint, login=login, password=password)
client.healthcheck()

experiment_name = 'experiment_ping'

while True:
    info = client.get_experiment_status(experiment_name)
    if info.status != ExperimentStatus.RUNNING:
        break
    time.sleep(10)


for report in info.execution_result:
    result, log = report.result
    if is_successful(result):
        data = result.unwrap()
        keys = data.keys()
        for k in keys:       
            result = data[k][0].unwrap()
            print(result.decode("utf-8"))
            print("\n\n")
    else:
        print("failed: ", result)
