#!/bin/bash

basepath=/workspaces/python

pip install -r "${basepath}/requirements.txt"

folder=$1

if [ -z "$folder" ]
then
    folder="${basepath}/config"
fi

echo "=> creating folder ${folder}"

mkdir -p "${folder}"

# Force Homeassistant to generate the configuration
hass -c "${folder}" &
pid=$(echo $!)
echo "=> HomeAssistant configuration generated with PID $pid"
sleep 1
kill $pid

echo "=> adding the custom component"
ln -s "${basepath}/custom_components" "${folder}/custom_components"

configured=$(grep file_transfer "${folder}/configuration.yaml")
if [ -z "$configured" ]
then
echo "=> configuring the custom component"
cat <<EOT >> "${folder}/configuration.yaml"

logger:
    default: info
    logs:
        custom_components.file_transfer: debug

# Configure the integration
file_transfer:
  # This is the global configuration that can be override with the sensor
  aws_endpoint_url:
  aws_bucket:
  aws_access_key_id:
  aws_secret_access_key:

# Add a new sensor
sensor:
  - platform: file_transfer
    entity_id: file_transfer_entity
    device_id: foo
    name: File transfer Entity
    # This is the optional sensor configuration that can be override with the service configuration (example in automations.yaml)
    aws_endpoint_url:
    aws_bucket:
    aws_access_key_id:
    aws_secret_access_key:
EOT

cat <<EOT > "${folder}/automations.yaml"
- alias: transfer_cam
  trigger:
    - platform: time_pattern
      minutes: "/1"
  action:
    - service: file_transfer.send_and_clean
      target:
        entity_id: sensor.file_transfer_entity
      data:
        local_folder: /var/log
        delete_after: false
        # This is the optional configuration. If not set, the sensor (or integration) configuration will be used
        aws_endpoint_url:
        aws_bucket:
        aws_access_key_id:
        aws_secret_access_key:
EOT
else
    echo "=> custom component is already configured"
fi

