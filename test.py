import os
import boto3
from botocore.exceptions import ClientError



class Foo:
    def transfer_files(self,
                       bucket:str,
                       folder:str,
                       endpoint_url:str=None,
                       aws_access_key_id:str=None,
                       aws_secret_access_key:str=None,
                       delete_after:bool=False)->bool:
        """transfert files from a folder to S3

        :param bucket:                 Bucket to upload to
        :param folder:                 Folder to scan
        :param endpoint_url:           AWS entrypoint
        :param aws_access_key_id:      Access key
        :param aws_secret_access_key:  Secret Key
        :return: True if file was uploaded, else False
        """
        files = self.scan_folder(folder)
        for object_name in files:
            if self.upload_file(
                file_name=files[object_name],
                bucket=bucket,
                object_name=object_name,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            ):
                if delete_after:
                    try:
                        os.remove(files[object_name])
                    except OSError as e:
                        return False

                return True
            else:
                return False

    def scan_folder(self, folder: str)->dict:
        """Scan a folder

        :param folder: Folder to scan
        :return: dictionary (object_name -> filename)
        """
        w = os.walk(folder)
        output=dict()
        for (dirpath, dirnames, filenames) in w:
            for filename in filenames:
                full_filename=("%s/%s"%(dirpath, filename))
                output[full_filename.lstrip(folder)] = full_filename
                print ("%s -> %s"%(full_filename.lstrip(folder),full_filename))
        return output

    def upload_file(self,
                    file_name:str,
                    bucket:str,
                    object_name:str=None,
                    endpoint_url:str=None,
                    aws_access_key_id:str=None,
                    aws_secret_access_key:str=None) -> bool:
        """Upload a file to an S3 bucket

        :param file_name:              File to upload
        :param bucket:                 Bucket to upload to
        :param object_name:            S3 object name. If not specified then file_name is used
        :param endpoint_url:           AWS entrypoint
        :param aws_access_key_id:      Access key
        :param aws_secret_access_key:  Secret Key
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = boto3.client(
                service_name='s3',
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            return False

        return True

Foo().transfer_files(
    bucket="test",
    folder="/workspaces/python/custom_components",
    endpoint_url="http://192.168.122.1:9000",
    aws_access_key_id="wedolowbelow",
    aws_secret_access_key="wedolowbelowsecret"
)