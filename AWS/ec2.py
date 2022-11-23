import boto3
from decouple import config
import traceback

class EC2():
    def __init__(self, max_num_instances = 8):
        self.__ec2_c = boto3.client(
        service_name='ec2',
        region_name=config('RegionName'),
        aws_access_key_id=config('AWSAccessKeyID'),
        aws_secret_access_key=config('AWSSecretKey')
        )
        self.__ec2 = boto3.resource(
        service_name='ec2',
        region_name=config('RegionName'),
        aws_access_key_id=config('AWSAccessKeyID'),
        aws_secret_access_key=config('AWSSecretKey')
        )
        self.__max_num_instances = max_num_instances
        
    def start_instance(self, index: int) -> bool:
        print("Enterd")
        try:
            print("Enterd2")
            instances_ids = []
            for i in range(index + 1, self.__max_num_instances + 1):
                instances_ids.append(config(f"Instance_{i}"))
            print("Enterd3")    
            print("Stop IDs: ", instances_ids)
            if instances_ids: self.__ec2_c.stop_instances(InstanceIds=instances_ids)
            print("Enterd4")  
            instances_ids = []
            for i in range(1, index + 1):
                instances_ids.append(config(f"Instance_{i}"))
            print("Enterd55")      
            print("Start IDs: ", instances_ids)
            if instances_ids: self.__ec2_c.start_instances(InstanceIds=instances_ids)
            print("Enterd6")  
            return True
        except Exception: 
            print(traceback.format_exc())
            print("Enterd7")  
            return False
            