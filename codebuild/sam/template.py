from troposphere import Template, Parameter, Sub, Ref
from troposphere.sqs import Queue
from troposphere.codebuild import Project, Artifacts, Environment, Source, SourceAuth, ProjectTriggers

from awacs.aws import Action, Allow, PolicyDocument, Principal, Statement, Policy
from troposphere.iam import Role, Policy as iamPolicy
from troposphere.s3 import Bucket

from awacs import sts , s3, iam, codebuild, logs

import json

STACK_NAME = Sub('${AWS::StackName}')

def code_build_service_role(artifact_bucket):
    return Role('CodeDeployRole', 
        RoleName=Sub('${AWS::StackName}-CodeDeploy-${AWS::Region}'),
        AssumeRolePolicyDocument=assume_role_policy_document("codebuild.amazonaws.com"),
        Policies=[iamPolicy(
            PolicyName=STACK_NAME,
            PolicyDocument=Policy(
                Statement=[
                    Statement(
                        Effect=Allow,
                        Resource= [ '*' ],
                        Action=[
                            logs.CreateLogGroup,
                            logs.CreateLogStream,
                            logs.PutLogEvents,
                        ],
                    ),
                    Statement(
                        Effect=Allow,
                        Resource= [ Sub("arn:aws:s3:::${ArtifactBucket}/*") ],
                        Action=[
                            s3.GetObject,
                            s3.GetObjectVersion,
                            s3.PutObject,
                        ],
                    ),
                ] 
            )
        )]
    )

def assume_role_policy_document(service_prinicpal):
    return Policy(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[sts.AssumeRole],
                Principal=Principal("Service", [service_prinicpal]),
            )
        ]
    )

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


    artifact_bucket =  t.add_resource(Bucket('ArtifactBucket'))
    
    cd_role = t.add_resource(code_build_service_role(artifact_bucket))

    code_build = t.add_resource(Project('CodeBuild',
        Name=STACK_NAME,
        Artifacts=Artifacts(
            Type='NO_ARTIFACTS',
        ),
        Environment=Environment(
            ComputeType='BUILD_GENERAL1_SMALL',
            Image='aws/codebuild/python:3.6.5',
            Type='LINUX_CONTAINER',
        ),
        ServiceRole=Ref(cd_role),
        Source=Source(
            Type='GITHUB',
            Auth=SourceAuth(
                Type='OAUTH',
            ),
            Location='https://github.com/karlw00t/aws-encryption-sdk-cli.git',
        ),
        Triggers=ProjectTriggers(
            Webhook=True,
        ),
    ))

    return t.to_dict()

if __name__ == "__main__": 
    print(json.dumps(create_template()))
