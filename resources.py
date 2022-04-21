
import boto3
from config import S3_BUCKET, S3_KEY, S3_SECRET

def get_s3_resource():
    """Set up S3 resource."""
    if S3_KEY and S3_SECRET:
        return boto3.resource('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    else:
        return boto3.resource('s3')
    
def get_bucket():
    """Get S3 bucket using S3 resource."""
    s3_resource = get_s3_resource()
    return s3_resource.Bucket(S3_BUCKET)