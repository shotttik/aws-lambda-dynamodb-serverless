import boto3
import json
from dotenv import load_dotenv
from os import getenv
import re
load_dotenv()
# Specify the IAM user or role ARN
entity_arn = 'arn:aws:iam::856718181672:instance-profile/LabInstanceProfile'
entity_arn = re.sub(r'[^a-zA-Z0-9+=,.@_-]', '', entity_arn)

# Specify the policy definition
policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Sid': 'AllowCreateRole',
            'Effect': 'Allow',
            'Action': 'iam:CreateRole',
            'Resource': 'arn:aws:iam::856718181672:role/rekognition-dev-IamRoleCustomResourcesLambdaExecut-*'
        }
    ]
}

# Create an IAM client
iam_client = boto3.client(
    "iam",
    aws_access_key_id=getenv("aws_access_key_id"),
    aws_secret_access_key=getenv("aws_secret_access_key"),
    aws_session_token=getenv("aws_session_token"),
    region_name=getenv("aws_region_name")
)

# Convert the policy to JSON string
policy_json = json.dumps(policy)

# Attach the policy to the user or role
response = iam_client.put_user_policy(
    UserName=entity_arn,
    PolicyName='AllowCreateRolePolicy',
    PolicyDocument=policy_json
)

# Alternatively, for a role:
# response = iam_client.put_role_policy(
#     RoleName=entity_arn,
#     PolicyName='AllowCreateRolePolicy',
#     PolicyDocument=policy_json
# )

print("Policy attached successfully.")
