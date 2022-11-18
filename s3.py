import boto3
from decouple import config

class S3():
    def __init__(self):
        self.__s3 = boto3.resource(
        service_name='s3',
        region_name=config('RegionName'),
        aws_access_key_id=config('AWSAccessKeyID'),
        aws_secret_access_key=config('AWSSecretKey')
        )
        self.__bucket = self.__s3.Bucket(config('BucketName'))
        
    def upload(self, file_obj: object, key: str) -> bool:
        try:
            self.__bucket.upload_fileobj(file_obj,key)
            return True
        except: return False
        
    def download(self, key: str, file_obj: object) -> bool:
        try:
            self.__bucket.download_fileobj(key,file_obj)
            return True
        except: return False
    
