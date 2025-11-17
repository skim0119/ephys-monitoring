import os
import time
import numpy as np

import matplotlib.pyplot as plt

from miv.mea import MEA
from miv.core.pipeline import Pipeline
from miv.io.openephys import Data, DataManager
from miv.signal.filter import ButterBandpass, MedianFilter
from miv.signal.spike import ThresholdCutoff
from miv.statistics import firing_rates

from miv.datasets.openephys_sample import load_data

import os
import datetime
import requests
import flask

from tkn import SLACK_BOT_TOKEN

SLACK_BOT_TOKEN += 'z'
CHANNEL = "nodes"
IMAGE_NAME = "result.png"
BOT_NAME = 'monitor'

def job_done(token):
    channel = 'nodes'
    texts = []
    texts.append(f'Job Done: {datetime.datetime.now()}')
    texts.append(f'    \n    From: {os.uname()}')
    text = '\n'.join(texts)

    #print(r.text)



def generate_activity():
    path = ""
    dm = DataManager(path)

    data = dm[-1]

    mea = MEA.return_mea("128_dual_connector_two_64_rhd")

    bandpass_filter = ButterBandpass(lowcut=400, highcut=1500, order=4)
    spike_detection = ThresholdCutoff(cutoff=4.0)
    data >> bandpass_filter >> spike_detection
    Pipeline(spike_detection).run(verbose=False)

    rates = firing_ratees(spike_detection)["rates"]

    X, Y, V = mea.map_data(rates)

    sc = plt.scatter(X.ravel(), Y.ravel(), c=V.ravel(), cmap="Oranges", vmin=0, vmax=20)
    plt.colorbar()
    plt.savefig(IMAGE_NAME, dpi=300)
    plt.cla()
    plt.clf()
    plt.close('all')

def upload_file():
    with open(IMAGE_NAME, 'rb') as f:
        response = requests.post(
            "https://slack.com/api/files.upload",
            headers={"Authorization": f"Bearer " + SLACK_BOT_TOKEN},
            data={"channels": CHANNEL, "title": "Update firing rate"},
            files={"file": f},
        )

    texts = []
    texts.append(f'Job Done: {datetime.datetime.now()}')
    texts.append(f'    \n    From: {os.uname()}')
    text = '\n'.join(texts)

    payload = {'token': SLACK_BOT_TOKEN, 'channel': CHANNEL, 'text': text, 'username': BOT_NAME}
    r = requests.post('https://slack.com/api/chat.postMessage', payload)


if __name__ == "__main__":
    S = 10 * 60
    while True:
        print("Generating and uploading activity.png ...")

        try:
            generate_activity()
            upload_file()
        except KeyboardInterrupt:
            break
        
        print(f"Done. Sleeping for 10 minutes.")

        time.sleep(S)  # 10 minute
