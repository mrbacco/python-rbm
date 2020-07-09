RCS BUSINESS MESSAGING: A TELCO AGENT

This sample RBM agent demonstrates how to use the RBM Python SDK to
create a simple telecommunications RBM agent


PREREQUISITES

You must have the following software installed on your development machine:

* [Python](https://www.python.org/downloads/) - version 3 or above
* [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)


SETUP

Prepare credentials:

1. Open the RBM Developer Console (https://rbm-console.sandbox.google.com/) with your RBM Platform
Google account and create a new RBM agent.

2. When the agent is available, click the agent's card.

3. In the left navigation, click **Service account**.

4. Click **Create key**, then click **Create**. Your browser downloads a service account key for
your agent. You need this key to make RBM API calls as your agent.

5. In this sample's root directory, create a "/resources" directory.

6. Rename the service account key "rbm-agent-service-account-credentials.json" and move it
into the "/resources" directory.


Prepare the sample:

1. In a terminal, navigate to this sample's root directory.

2. Run the following commands:

virtualenv env
source env/bin/activate
pip install -t lib -r requirements.txt



DEPLOY TO GOOGLE CLOUD

1. In a terminal, navigate to this sample's root directory.

2. Run the following gcloud command:

gcloud config set project YOUR-GCP-PROJECT-ID

Replace YOUR-GCP-PROJECT-ID with your project's ID.

3. Run the following to deploy the code:

gcloud app deploy --quiet

4. Navigate to https://YOUR-GCP-PROJECT-ID.appspot.com


SETUP THE AGENT WEBHOOK

1. Return to the RBM Developer Console, in the left navigation, click **Integrations**.

2. Click Edit subscription and configure a push subscription with a
URL of https://YOUR-GCP-PROJECT-ID.appspot.com/callback

