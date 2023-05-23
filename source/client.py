import asyncio
import os
import boto3
from os import getenv
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import sys
from urllib.request import urlopen
from logger import CustomLogger
import re

LOGGER = CustomLogger.get_logger(__name__)
load_dotenv()


class Client:

    def __init__(self, bucket_name=""):
        LOGGER.info('Logging in aws client.')
        try:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=getenv("aws_access_key_id"),
                aws_secret_access_key=getenv("aws_secret_access_key"),
                aws_session_token=getenv("aws_session_token"),
                region_name=getenv("aws_region_name")
            )
            self.bucket_name: str = bucket_name
            self.client.list_buckets()["Buckets"]
            LOGGER.info('Successfully logged in aws client.')

        except ClientError as e:
            LOGGER.error(e)
            sys.exit()
        except Exception:
            LOGGER.error("Unexpected error")
            sys.exit()

    # upload images from directory

    async def upload_image_to_s3(self, file_path):
        s3 = boto3.client('s3')
        destination_path = os.path.basename(file_path)

        await asyncio.to_thread(s3.upload_file, file_path, self.bucket_name, destination_path)
        print(f"Uploaded: {file_path}")
        file_name = file_path.split("\\")[-1]
        # self.set_object_access_policy(file_name)

    async def recursive_image_upload(self, directory):
        tasks = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    file_path = os.path.join(root, file)
                    print(file_path)
                    task = self.upload_image_to_s3(file_path)
                    tasks.append(task)

        await asyncio.gather(*tasks)

    def set_object_access_policy(self, file_name):
        print(file_name)
        try:
            response = self.client.put_object_acl(
                ACL="public-read",
                Bucket=self.bucket_name,
                Key=file_name
            )
        except ClientError as e:
            LOGGER.error(e)
            return False
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code == 200:
            return True
        return False
