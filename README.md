# IntelliZone CAN Device Implementation
## Overview
This project implements an IntelliZone CAN device using Python. It provides a basic framework for communicating with a controller via the CAN bus protocol.

## Features

Node discovery and configuration
Heartbeat messaging
Status request and response handling
Support for multiple module types and message types

## Requirements

- Python 3.x
- python-can library (version 4.5.0 or later)
- bidict library (version 0.23.1 or later)
- spidev library (version 3.6 or later)

## Installation

1. Clone the repository: [git clone https://github.com/your-repo/intellizone-can-device.git](https://github.com/your-repo/intellizone-can-device.git)
2. Install the required libraries: pip install -r requirements.txt
3. Configure the config_yaml.py file with your device's Unique ID (UID) and other settings.

## Usage

1. Run the main script: python main.py
2. The device will perform node discovery and start sending heartbeat messages to the controller.
3. Use the status_request module to send status requests to the controller and receive responses.

## Modules

- can_interface: Provides a basic interface for interacting with the CAN bus.
- messages: Defines the message structures and types used in the project.
- node_discovery: Handles node discovery and configuration.
- status_listener: Listens for status responses from the controller.
- status_request: Sends status requests to the controller.

## Configuration

The config_yaml.py file contains settings for the device, including the UID, module type, and message types. Modify this file to suit your device's needs.

## Troubleshooting

- Check the logs for errors and warnings.
- Verify that the CAN bus interface is properly configured.
- Use a CAN bus analyzer tool to inspect the messages being sent and received.

## Contributing

Contributions are welcome! Please submit pull requests with clear descriptions of the changes made.
