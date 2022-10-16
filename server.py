import socket
import threading

PORT = 9002
HOST = '192.168.1.253'
FORMAT = 'utf-8'
TERMINATE = b'TERMINATE'
HEADER = 64


def handleClient(conn, addr, clients):
    while True:
        # header
        header = conn.recv(HEADER)
        if not header:
            continue

        msgLength = int(header)
        msg = conn.recv(msgLength)

        if msg == TERMINATE:
            break

        print(f'{addr} -> {msg.decode(FORMAT)}')
        for client in clients:
            if client != conn:
                # don't send message to itself
                send(client, addr, msg)

    print(f'[DEBUG] {addr} exited...')
    conn.close()


def send(conn, sender, encodedMsg):
    encodedMsg = str(sender).encode(FORMAT) + b' -> ' + encodedMsg
    msgLength = str(len(encodedMsg)).encode(FORMAT)
    if len(msgLength) < HEADER:
        msgLength += b' ' * (HEADER - len(msgLength))

    # header
    conn.send(msgLength)

    # actual message
    conn.send(encodedMsg)


def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    clients = set()

    try:
        while True:
            conn, addr = server.accept()
            print(f'[DEBUG] {addr} joined...')
            clients.add(conn)
            threading.Thread(
                target=handleClient,
                args=(conn, addr, clients)).start()
    except KeyboardInterrupt:
        print('Shuting down server...')
    except Exception as e:
        print(e)
    finally:
        server.close()


if __name__ == '__main__':
    start()
