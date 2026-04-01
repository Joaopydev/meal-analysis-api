import aioboto3

def get_sqs_client():
    session = aioboto3.Session()
    return session.client("sqs")