from troposphere import Template, Parameter
from troposphere.sqs import Queue

from troposphere.s3 import Bucket

import json

def create_template():
    t = Template()


    oauth_token = t.add_parameter(Parameter(
        "GitHubOAuthToken",
        Description="Secret for github",
        Type="AWS::SSM::Parameter::Value<String>",
        Default="oauth",
        NoEcho=True,
    ))

    owner = t.add_parameter(Parameter(
        "Owner",
        Type="String",
    ))

    repo = t.add_parameter(Parameter(
        "Repo",
        Type="String",
    ))

    branch = t.add_parameter(Parameter(
        "Branch",
        Type="String",
    ))


    artifact_bucket =  t.add_resource(Bucket('ArtifactBucket',
    ))

    return t.to_dict()

if __name__ == "__main__": 
    print(json.dumps(create_template()))
