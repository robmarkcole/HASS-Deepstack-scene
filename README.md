# HASS-Deepstack-scene
[Home Assistant](https://www.home-assistant.io/) custom component for Deepstack scene recognition. Deepstack is a service which runs in a docker container and exposes deep-learning models via a REST API. Deepstack [scene recognition](https://python.deepstack.cc/scene-recognition) classifies an image into one of 365 scenes. This integration adds an image processing entity with state that is the most likely scene for the image. **Note** that by default the component will **not** automatically scan images, but requires you to call the `image_processing.scan` service e.g. using an automation triggered by motion.


## Home Assistant setup
Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder). Then configure the integration. Add to your Home-Assistant config:

```yaml
image_processing:
  - platform: deepstack_scene
    ip_address: localhost
    port: 5000
    api_key: mysecretkey
    source:
      - entity_id: camera.local_file
```

Configuration variables:
- **ip_address**: the ip address of your deepstack instance.
- **port**: the port of your deepstack instance.
- **api_key**: (Optional) Any API key you have set.
- **timeout**: (Optional, default 10 seconds) The timeout for requests to deepstack.
- **source**: Must be a camera.
- **name**: (Optional) A custom name for the the entity.