import socket
import threading

PORT = 9002
HOST = '192.168.1.253'
FORMAT = 'utf-8'
TERMINATE = 'TERMINATE'
HEADER = 64


def send(conn, msg):
    encodedMsg = msg.encode(FORMAT)
    msgLength = str(len(encodedMsg)).encode(FORMAT)
    if len(msgLength) < HEADER:
        msgLength += b' ' * (HEADER - len(msgLength))

    # header
    conn.send(msgLength)

    # actual message
    conn.send(encodedMsg)


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((HOST, PORT))
    except ConnectionRefusedError:
        print('Server is down')
        server.close()
        return

    threading.Thread(target=recieve, args=(server, )).start()
    while True:
        msg = input()
        if msg == TERMINATE:
            server.close()
            return

        send(server, msg)


def recieve(conn):
    while True:
        header = conn.recv(HEADER)
        if not header:
            continue
        msgLength = int(header)
        msg = conn.recv(msgLength)

        print(msg.decode(FORMAT))


if __name__ == '__main__':
    start()
