""" Panoptes - AWS - Authentication

Using AWS best practices forcing the user to write Named Profiles instead of
direct IAM credentials through CLI.
"""

import boto3
import panoptes.generic.exceptions


def create_session(region, profile=None, session_token=None):
    """
    Generates a Boto3 session from named profile and region inputs
    """
    aws_session = boto3.Session(
        profile_name=profile,
        region_name=region,
        aws_session_token=session_token,
    )
    if not aws_session.get_credentials():
        raise panoptes.generic.exceptions.PanoptesAuthError(
            "Panoptes could not authenticate to AWS. "
            "Check if your credentials exist and work."
        )
    return aws_session


def get_session_info(aws_session):
    """
    Get ARN from the current session
    """
    return aws_session.client('sts').get_caller_identity()['Arn']


if __name__ == "__main__":
    pass
