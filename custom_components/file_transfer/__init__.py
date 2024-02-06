""" Implements the VersatileThermostat sensors component """
import logging

from homeassistant.core import (
    HomeAssistant,
    callback
)
from homeassistant.config_entries import ConfigEntry



import voluptuous as vol
import homeassistant.helpers.config_validation as cv



from .const import (
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(
    hass: HomeAssistant, config: ConfigEntry
):  # pylint: disable=unused-argument
    """Initialisation de l'intégration"""
    _LOGGER.info(
        "Initializing %s integration with plaforms: %s with config: %s",
        DOMAIN,
        PLATFORMS,
        config,
    )

    # Mettre ici un eventuel code permettant l'initialisation de l'intégration
    # Ca peut être une connexion sur le Cloud qui fournit les données par ex
    # (pas nécessaire pour le tuto)

    # L'argument config contient votre fichier configuration.yaml
    my_config = config.get(DOMAIN)  # pylint: disable=unused-variable

    # aws_endpoint_url=my_config.get(AWS_ENDPOINT_URL)
    # aws_bucket=my_config.get(AWS_BUCKET)
    # aws_access_key_id=my_config.get(AWS_ACCESS_KEY)
    # aws_secret_access_key=my_config.get(AWS_SECRET_ACCESS_KEY)

    _async_setup_shared_data(hass, my_config)

    # Return boolean to indicate that initialization was successful.
    return True

@callback
def _async_setup_shared_data(hass: HomeAssistant, config: any) -> bool:
    """Create shared data for platform config and rest coordinators."""
    hass.data[DOMAIN] = config