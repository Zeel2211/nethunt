import socket
import sys
import threading
import getopt
import subprocess

# Global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("Net Hunter Tool")
    print("Usage : nethunt.py -t target_host -p port")
    print("-l --listen                   - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run     - execute the given file upon receiving a connection")
    print("-c --command                 - initialize a command shell")
    print("-u --upload=destination      - upon receiving connection upload a file and write to [destination]")
    print(" ")
    print("Examples:")
    print("nethunt.py -t 192.168.0.1 -p 5555 -l -c")
    print("nethunt.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("nethunt.py -t 192.168.0.1 -p 5555 -e='cat /etc/passwd'")
    print("echo 'ABCDE' | ./nethunt.py -t 192.168.0.1 -p 135")
    sys.exit()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode())

        while True:
            response = ""

            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data.decode()
                if len(data) < 4096:
                    break

            print(response, end='')

            buffer = input("")
            if buffer.lower() == 'exit':  # Gracefully handle exit
                break
            buffer += "\n"
            client.send(buffer.encode())
    except Exception as e:
        print(f"[*] Exception! Exiting. Error: {e}")
    finally:
        client.close()

def server_loop():
    global target

    if not target:
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((target, port))
    except Exception as e:
        print(f"[!!] Failed to bind to {target}:{port}. Error: {e}")
        sys.exit()

    server.listen(5)
    print(f"[*] Listening on {target}:{port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    except Exception as e:
        output = f"Failed to execute command. Error: {e}\r\n".encode()
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command
    global upload_destination

    # File upload handling
    if upload_destination:
        file_buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data
        try:
            with open(upload_destination, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Successfully saved file to {upload_destination}\r\n".encode())
        except Exception as e:
            client_socket.send(f"Failed to save file to {upload_destination}. Error: {e}\r\n".encode())

    # Execute command if specified
    if execute:
        output = run_command(execute)
        client_socket.send(output)

    # Shell mode
    if command:
        while True:
            client_socket.send(b"<NetHunt:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()
            response = run_command(cmd_buffer)
            client_socket.send(response)

def main():
    global listen
    global command
    global execute
    global target
    global upload_destination
    global port

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", [
            "help", "listen", "execute=", "target=", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # Client sender mode
    if not listen and target and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    # Server loop
    if listen:
        server_loop()

if __name__ == "__main__":
    main()
