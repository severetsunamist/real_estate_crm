from .base import *

DEBUG = False

# Production security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Use S3 storage if credentials are provided
if (os.getenv('CLOUD_RU_ACCESS_KEY_ID') and 
    os.getenv('CLOUD_RU_SECRET_ACCESS_KEY') and 
    os.getenv('CLOUD_RU_BUCKET_NAME')):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'