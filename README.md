# File Transfer

Deep scan a directory and send files to a S3 bucket (AWS or custom). After sending files the local version can be deleted.

- Integration: `file_transfer`
- Platform: `file_transfer`
- Service: `file_transfer.send_and_clean`

The bucket must be previously created.

# Example configuration

In configuration.yaml:

```yaml
file_transfer:
  aws_endpoint_url: https://s3.gra.io.cloud.ovh.net
  aws_access_key_id: my_access
  aws_secret_access_key: insecure

sensor:
  - platform: file_transfer
    entity_id: file_transfer_entity
    device_id: foo
    name: File transfer Entity
    #aws_endpoint_url: https://s3.gra.io.cloud.ovh.net
    aws_bucket: test
    #aws_access_key_id: my_access
    #aws_secret_access_key: insecure
```

In automations.yaml:

```yaml
- alias: transfer_cam
  trigger:
    - platform: time_pattern
      minutes: "/1"
  action:
    - service: file_transfer.send_and_clean
      target:
        entity_id: sensor.file_transfer_entity
      data:
        local_folder: /workspaces/python/test
        delete_after: false
        # aws_endpoint_url: https://s3.gra.io.cloud.ovh.net
        # aws_bucket: test
        # aws_access_key_id: my_access
        # aws_secret_access_key: insecure
```