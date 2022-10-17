import socket
import threading


class Server:
    FORMAT = 'utf-8'
    TERMINATE = b'TERMINATE'
    HEADER = 64

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = set()

    def handleClient(self, conn, addr):
        while True:
            # header
            header = conn.recv(self.HEADER)
            if not header:
                # when conneted the first message will be blank, so skip this
                continue

            msgLength = int(header)
            msg = conn.recv(msgLength)

            if msg == self.TERMINATE:
                self.clients.remove(conn)
                return

            print(f'{addr} -> {msg.decode(self.FORMAT)}')

            disconnectedClients = set()
            for client in self.clients:
                if client != conn:
                    # don't send message to itself
                    try:
                        self.send(client, addr, msg)
                    except BrokenPipeError:
                        # disconnected by connection lost
                        disconnectedClients.add(client)

            self.clients.difference_update(disconnectedClients)

        # disconnected by TERMINATE
        conn.close()

    def send(self, conn, sender, encodedMsg):
        encodedMsg = str(sender).encode(self.FORMAT) + b' -> ' + encodedMsg
        msgLength = str(len(encodedMsg)).encode(self.FORMAT)
        if len(msgLength) < self.HEADER:
            msgLength += b' ' * (self.HEADER - len(msgLength))

        # header
        conn.send(msgLength)

        # actual message
        conn.send(encodedMsg)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen()

            while True:
                conn, addr = server.accept()
                print(f'[DEBUG] {addr} joined...')
                self.clients.add(conn)
                threading.Thread(
                    target=self.handleClient,
                    args=(conn, addr)).start()


if __name__ == '__main__':
    host = input('Host: ')  # '192.168.1.253'
    port = int(input('Port: '))  # 9002

    server = Server(host, port)
    server.start()
