# Custom components for Home Assistant

[![maintainer](https://img.shields.io/badge/maintainer-Sander%20Huisman%20-blue.svg?style=for-the-badge)](https://github.com/Sanderhuisman)

## About

This repository contains the docker monitor component I developed for my own [Home-Assistant](https://www.home-assistant.io) setup. Feel free to use the component and report bugs if you find them. If you want to contribute, please report a bug or pull request and I will reply as soon as possible. Please star & watch my project such I can see how many people like my components and for you to stay in the loop as updates come along.

## Docker Monitor

The Docker monitor allows you to monitor statistics and turn on/off containers. The monitor can connected to a daemon through the url parameter. When home assistant is used within a Docker container, the daemon can be mounted as follows `-v /var/run/docker.sock:/var/run/docker.sock`. The monitor is based on [Glances](https://github.com/nicolargo/glances) and [ha-dockermon](https://github.com/philhawthorne/ha-dockermon) and combines (in my opinion the best of both integrated in HA :)).

### Events

The monitor can listen for events on the Docker event bus and can fire an event on the Home Assistant Bus. The monitor will use the following event:

* `{name}_container_event` with name the same set in the configuration.

The event will contain the following data:

* `Container`: Container name
* `Image`: Container image
* `Status`: Container satus
* `Id`: Container ID (long)

### Configuration

To use the `docker_monitor` in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
docker_monitor:
  hosts:
    - url: unix://var/run/docker.sock
      name: Docker
      event: true
      monitored_conditions:
        - version
      containers:
        homeassistant_homeassistant_1:
          switch: False
          sensors:
            - status
            - uptime
            - cpu_percentage_usage
            - memory_usage
            - memory_percentage_usage
            - network_total_up
            - network_total_down
        homeassistant_database_1:
          switch: False
          sensors:
            - status
            - uptime
            - cpu_percentage_usage
            - memory_usage
            - memory_percentage_usage
            - network_total_up
            - network_total_down
        homeassistant_mosquitto_1:
          switch: True
          sensors:
            - status
            - uptime
            - cpu_percentage_usage
            - memory_usage
            - memory_percentage_usage
            - network_total_up
            - network_total_down
```

#### Configuration variables

| Parameter            | Type                     | Description                                                           |
| -------------------- | ------------------------ | --------------------------------------------------------------------- |
| name                 | string       (Required)  | Client name of Docker daemon. Defaults to `Docker`.                   |
| url                  | string       (Required)  | Host URL of Docker daemon. Defaults to `unix://var/run/docker.sock`.  |
| event                | boolean      (Optional)  | Listen for events from Docker. Defaults to false.                     |
| scan_interval        | time_period  (Optional)  | Update interval. Defaults to 10 seconds.                              |
| monitored_conditions | list         (Optional)  | Array of conditions to be monitored. Defaults to all conditions       |
| containers           | list         (Required)  | Array of containers to monitor. Defaults to all containers.           |

| Monitored Conditions              | Description                     | Unit  |
| --------------------------------- | ------------------------------- | ----- |
| version                           | Docker version                  | -     |
| containers_total                  | Total number of containers      | -     |
| containers_paused                 | Number of paused containers     | -     |
| containers_running                | Number of running containers    | -     |
| containers_stopped                | Number of stopped containers    | -     |
| images_total                      | Total number of images          | -     |

| Container Conditions              | Description                     | Unit  |
| --------------------------------- | ------------------------------- | ----- |
| status                            | Container status                | -     |
| uptime                            | Container start time            | -     |
| image                             | Container image                 | -     |
| cpu_percentage_usage              | CPU usage                       | %     |
| memory_usage                      | Memory usage                    | MB    |
| memory_percentage_usage           | Memory usage                    | %     |
| network_total_up                  | Network total upstream          | MB    |
| network_total_down                | Network total downstream        | MB    |

## Credits

* [frenck](https://github.com/frenck/home-assistant-config)
* [robmarkcole](https://github.com/robmarkcole/Hue-sensors-HASS)
