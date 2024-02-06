""" Implements the VersatileThermostat sensors component """
import logging

from homeassistant.core import (
    HomeAssistant
)
from homeassistant.const import (
    UnitOfInformation,
    CONF_NAME,
    CONF_ENTITY_ID,
)
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

import voluptuous as vol
import homeassistant.helpers.config_validation as cv


from .const import (
    SERVICE_FILE_TRANSFER,
    DOMAIN,
    AWS_BUCKET,
    AWS_ENDPOINT_URL,
    AWS_ACCESS_KEY,
    AWS_SECRET_ACCESS_KEY,
    LOCAL_FOLDER,
    DELETE_AFTER,
)

import os
import boto3
from botocore.exceptions import ClientError

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,  # pylint: disable=unused-argument
):
    """Configuration de la plate-forme tuto_hacs à partir de la configuration
    trouvée dans configuration.yaml"""

    _LOGGER.debug("Calling async_setup_entry entry=%s", entry)

    entity = SensorFileTransfer(hass, entry)
    async_add_entities([entity], True)

    # Add services
    platform = async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_FILE_TRANSFER,
        {
            vol.Required(LOCAL_FOLDER): cv.string,
            vol.Optional(AWS_ENDPOINT_URL): cv.string,
            vol.Optional(AWS_BUCKET): cv.string,
            vol.Optional(AWS_ACCESS_KEY): cv.string,
            vol.Optional(AWS_SECRET_ACCESS_KEY): cv.string,
            vol.Optional(DELETE_AFTER): cv.boolean,
        },
        "service_file_transfer",
    )


class SensorFileTransfer(SensorEntity):
    """La classe de l'entité File Transfer"""

    _hass: HomeAssistant
    _aws_endpoint_url: str
    _aws_bucket: str
    _aws_access_key_id: str
    _aws_secret_access_key: str

    def __init__(
        self,
        hass: HomeAssistant,  # pylint: disable=unused-argument
        entry_infos: ConfigEntry,  # pylint: disable=unused-argument
    ) -> None:
        """Initisalisation de notre entité"""
        self._attr_name = entry_infos.get(CONF_NAME)
        self._attr_unique_id = entry_infos.get(CONF_ENTITY_ID)
        self._attr_has_entity_name = True
        self._attr_native_value = 0
        self._hass = hass


        sensor_aws_endpoint_url = entry_infos.get(AWS_ENDPOINT_URL)
        sensor_aws_bucket = entry_infos.get(AWS_BUCKET)
        sensor_aws_access_key_id = entry_infos.get(AWS_ACCESS_KEY)
        sensor_aws_secret_access_key = entry_infos.get(AWS_SECRET_ACCESS_KEY)

        if DOMAIN in hass.data:
            integration_data = hass.data[DOMAIN]

            self._aws_endpoint_url=integration_data.get(AWS_ENDPOINT_URL)
            if sensor_aws_endpoint_url is not None and sensor_aws_endpoint_url != "":
                self._aws_endpoint_url = sensor_aws_endpoint_url

            self._aws_bucket=integration_data.get(AWS_BUCKET)
            if sensor_aws_bucket is not None and sensor_aws_bucket != "":
                self._aws_bucket = sensor_aws_bucket

            self._aws_access_key_id=integration_data.get(AWS_ACCESS_KEY)
            if sensor_aws_access_key_id is not None and sensor_aws_access_key_id != "":
                self._aws_access_key_id = sensor_aws_access_key_id

            self._aws_secret_access_key=integration_data.get(AWS_SECRET_ACCESS_KEY)
            if sensor_aws_secret_access_key is not None and sensor_aws_secret_access_key != "":
                self._aws_secret_access_key = sensor_aws_secret_access_key


    @property
    def icon(self) -> str | None:
        return "mdi:account-file"

    @property
    def device_class(self) -> SensorDeviceClass | None:
        return SensorDeviceClass.DATA_SIZE

    @property
    def native_unit_of_measurement(self) -> str | None:
        return UnitOfInformation.MEGABITS

    @property
    def state_class(self) -> SensorStateClass | None:
        return SensorStateClass.TOTAL

    @property
    def should_poll(self) -> bool:
        """Do not poll for those entities"""
        return False

    def transfer_files(self,
                       aws_bucket:str,
                       local_folder:str,
                       aws_endpoint_url:str=None,
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
        _LOGGER.debug("scanning folder %s"%(local_folder))
        files = self.scan_folder(local_folder)
        for object_name in files:
            _LOGGER.debug("file %s -> %s"%(files[object_name], object_name))

            if self.upload_file(
                file_name=files[object_name],
                aws_bucket=aws_bucket,
                object_name=object_name,
                aws_endpoint_url=aws_endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            ):
                try:
                    file_stats = os.stat(files[object_name])
                    self._attr_native_value = self._attr_native_value + (file_stats.st_size * 1e-9)
                except OSError as e:
                    _LOGGER.error("removing file %s: %s", files[object_name], e)

                if delete_after:
                    _LOGGER.debug("removing file %s"%(files[object_name]))
                    try:
                        os.remove(files[object_name])
                    except OSError as e:
                        _LOGGER.error("removing file %s: %s", files[object_name], e)
                        return False
            else:
                return False

        self.async_write_ha_state()
        _LOGGER.debug("success: %d files"%(len(files)))


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
                object_name=os.path.relpath(full_filename, folder)
                output[object_name] = full_filename
                print ("%s -> %s"%(full_filename.lstrip(folder),full_filename))
        return output

    def upload_file(self,
                    file_name:str,
                    aws_bucket:str,
                    object_name:str=None,
                    aws_endpoint_url:str=None,
                    aws_access_key_id:str=None,
                    aws_secret_access_key:str=None) -> bool:
        """Upload a file to an S3 bucket

        :param file_name:              File to upload
        :param aws_bucket:             Bucket to upload to
        :param object_name:            S3 object name. If not specified then file_name is used
        :param aws_endpoint_url:       AWS entrypoint
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
                endpoint_url=aws_endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        try:
            response = s3_client.upload_file(file_name, aws_bucket, object_name)
        except ClientError as e:
            _LOGGER.error("uploading file %s: %s", file_name, e)
            return False

        return True

    async def service_file_transfer(self,
                              local_folder:str,
                              aws_endpoint_url: str=None,
                              aws_bucket: str=None,
                              aws_access_key_id: str=None,
                              aws_secret_access_key: str=None,
                              delete_after: bool=None):
        current_aws_endpoint_url= self._aws_endpoint_url
        if aws_endpoint_url is not None and aws_endpoint_url != "":
            current_aws_endpoint_url = aws_endpoint_url

        current_aws_bucket= self._aws_bucket
        if aws_bucket is not None and aws_bucket != "":
            current_aws_bucket = aws_bucket

        current_aws_access_key_id= self._aws_access_key_id
        if aws_access_key_id is not None and aws_access_key_id != "":
            current_aws_access_key_id = aws_access_key_id

        current_aws_secret_access_key= self._aws_secret_access_key
        if aws_secret_access_key is not None and aws_secret_access_key != "":
            current_aws_secret_access_key = aws_secret_access_key

        _LOGGER.debug("transfering files fom %s to %s@%s"%(local_folder, current_aws_endpoint_url, current_aws_bucket))
        self.transfer_files(aws_bucket=current_aws_bucket,
                       local_folder=local_folder,
                       aws_endpoint_url=current_aws_endpoint_url,
                       aws_access_key_id=current_aws_access_key_id,
                       aws_secret_access_key=current_aws_secret_access_key,
                       delete_after=delete_after)


