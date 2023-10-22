from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    file_overwrite = True



class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = True

