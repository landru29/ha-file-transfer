""" Les constantes pour l'intégration Tuto HACS """

from homeassistant.const import Platform

DOMAIN = "file_transfer"


SERVICE_FILE_TRANSFER = "send_and_clean"
PLATFORMS: list[Platform] = [Platform.SENSOR]

AWS_ENDPOINT_URL="aws_endpoint_url"
AWS_BUCKET="aws_bucket"
AWS_ACCESS_KEY="aws_access_key_id"
AWS_SECRET_ACCESS_KEY="aws_secret_access_key"
LOCAL_FOLDER="local_folder"
DELETE_AFTER="delete_after"