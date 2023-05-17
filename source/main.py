import asyncio
from logger import CustomLogger
from dotenv import load_dotenv
import argparse
from client import Client
LOGGER = CustomLogger.get_logger(__name__)
load_dotenv()


def main(command_line=None):
    parser = argparse.ArgumentParser('AWS S3 Client BTU TASK')
    subparsers = parser.add_subparsers(dest='command')
    bucket = subparsers.add_parser('bucket', help='work with bucket')
    bucket.add_argument(
        '--name',
        type=str, help="Enter Bucket Name", required=True
    )
    group = bucket.add_mutually_exclusive_group()
    group.add_argument("-upload",
                       "--upload"
                       "-u",
                       action='store_true',
                       dest="upload",
                       help="Upload files from directory myauto",
                       )
    args = parser.parse_args(command_line)

    if args.command == 'bucket':
        if args.name and args.upload:
            print(args.name)
            s3_client = Client(args.name)
            asyncio.run(s3_client.recursive_image_upload('downloaded_images'))


if __name__ == '__main__':
    main()
