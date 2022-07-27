#!/usr/bin/env python
import os

import requests
import boto3
from botocore.exceptions import ClientError

GROUP_ID = os.environ['AWS_SECURITY_GROUP_ID']
PORT = os.environ['PORT']
RULE_DESCRIPTION = os.environ['RULE_DESCRIPTION']
ec2 = boto3.client(
    "ec2",
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION'],
)


def get_new_ip():
    return requests.get("https://checkip.amazonaws.com").text[:-1] + "/32"


def get_old_ip():
    try:
        response = ec2.describe_security_groups(GroupIds=[GROUP_ID])
    except ClientError as e:
        raise

    security_groups = response["SecurityGroups"]

    for el in range(len(security_groups)):
        if security_groups[el]["GroupId"] == GROUP_ID:
            ip_pems = security_groups[el]["IpPermissions"]

            for i in range(len(ip_pems)):
                if ip_pems[i]["IpRanges"][0].get("Description") == RULE_DESCRIPTION:
                    return ip_pems[i]["IpRanges"][0]["CidrIp"]

    return None


def remove_old_rule(old_ip):
    try:
        d = ec2.revoke_security_group_ingress(
            GroupId=GROUP_ID,
            IpPermissions=[
                {
                    "FromPort": PORT,
                    "ToPort": PORT,
                    "IpProtocol": "tcp",
                    "IpRanges": [{"CidrIp": old_ip, "Description": RULE_DESCRIPTION}],
                }
            ],
        )

        print("Old rule successfully removed: %s" % d)
    except ClientError:
        raise


def create_new_rule(new_ip):
    try:
        d = ec2.authorize_security_group_ingress(
            GroupId=GROUP_ID,
            IpPermissions=[
                {
                    "FromPort": PORT,
                    "ToPort": PORT,
                    "IpProtocol": "tcp",
                    "IpRanges": [{"CidrIp": new_ip, "Description": RULE_DESCRIPTION}],
                }
            ],
        )

        print("New rule successfully created: %s" % d)
    except ClientError:
        raise


if __name__ == '__main__':
    old_ip_address = get_old_ip()
    new_ip_address = get_new_ip()

    if old_ip_address and old_ip_address != new_ip_address:
        remove_old_rule(old_ip_address)
        create_new_rule(new_ip_address)
        print("OK")
    elif old_ip_address:
        # old IP is the same as the new one
        print("IP already up-to-date")
    else:
        # couldn't determine old IP
        print("Couldn't determine the old IP. Your rule (matching the description) should already exist.")
