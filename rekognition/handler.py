import json
import os
import urllib
import uuid
import boto3
import requests
import time
# https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html


def get_image_labels(bucket, key):
    rekognition_client = boto3.client('rekognition')
    response = rekognition_client.detect_labels(
        Image={'S3Object': {
            'Bucket': bucket,
            'Name': key
        }}, MaxLabels=10)

    return response


def make_item(data):
    if isinstance(data, dict):
        return {k: make_item(v) for k, v in data.items()}

    if isinstance(data, list):
        return [make_item(v) for v in data]

    if isinstance(data, float):
        return str(data)

    return data


def put_labels_in_db(data, media_name, media_bucket, env_table):
    data.pop('ResponseMetadata', None)

    if 'JobStatus' in data:
        del data['JobStatus']
        data['mediaType'] = 'Image'

    data['mediaName'] = media_name
    data['mediaBucket'] = media_bucket

    data['id'] = str(uuid.uuid1())

    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ[env_table]
    data_base = dynamodb.Table(table_name)

    data = make_item(data)

    data_base.put_item(Item=data)

    return


# Lambda events


def lambda_handler(event, context):
    for record in event['Records']:
        objectExtenstion = record['s3']['object']['key'].split('.')[-1]
        # https://t.ly/C5T-
        if objectExtenstion not in ['jpeg', 'png', 'jpg', 'gif']:
            print('file extension doesn`t supports.')
            continue

        bucket_name = record['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(
            record['s3']['object']['key'])

        bucket_location = boto3.client(
            's3').get_bucket_location(Bucket=bucket_name)
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location['LocationConstraint'],
            bucket_name,
            object_key)

        response = requests.post(
            'https://carnet.ai/recognize-url', data=object_url)
        status_code = response.status_code

        if status_code == 200:
            json_data = response.json()
            print(json_data)
            # saving data from carnet
            put_labels_in_db(json_data, object_key,
                             bucket_name, "DYNAMO_DB_TABLE")
        elif status_code == 429:
            print("Bad API response: 429. Retrying after half a second...")
            time.sleep(0.5)
        elif status_code == 500:
            err = "Image doesn't contain a car"
            if response.json()['error'] == err:
                # saving data from recognize
                put_labels_in_db(get_image_labels(bucket_name, object_key), object_key,
                                 bucket_name, "SECOND_DYNAMO_DB_TABLE")
            else:
                print(f"Bad API response: {status_code}")
        else:
            print(f"Bad API response: {status_code}")

    return
