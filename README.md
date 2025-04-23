# Net Hunter Tool

The **Net Hunter Tool** is a Python-based networking tool that can be used for remote access, file upload, command execution, and interaction with remote systems via sockets. It can act as both a server and a client, and supports functionalities such as listening for incoming connections, uploading files, running commands, and providing a command shell.

## Features
- **Server Mode**: Listen for incoming connections and interact with clients.
- **Client Mode**: Send data to a remote server and execute commands.
- **File Upload**: Upload a file to the target machine and save it to a specified destination.
- **Command Execution**: Execute a specified command on the target machine and get the result.
- **Command Shell**: Provides a basic interactive shell to execute commands remotely.

## Requirements
- Python 3.x
- `socket` and `subprocess` modules (built-in with Python)
  
## Usage

### Command-line Options

- **-l, --listen**: Start the tool in listen mode to accept incoming connections on the specified host and port.
- **-e, --execute=FILE**: Execute the specified file upon receiving a connection.
- **-c, --command**: Start a command shell on the target machine after connection.
- **-u, --upload=DESTINATION**: Upload a file from the client to the specified destination on the target machine.
- **-t, --target=TARGET**: Specify the target host (IP address or domain).
- **-p, --port=PORT**: Specify the port number to use for the connection.

### Examples

- **Start listening on a specific host and port and initialize a command shell**:
  ```bash
  python3 nethunt.py -t 192.168.0.1 -p 5555 -l -c
