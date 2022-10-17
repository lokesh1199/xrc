import socket
import threading


class Client:
    FORMAT = 'utf-8'
    TERMINATE = 'TERMINATE'
    HEADER = 64

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.die = threading.Event()    # event to check is client up

    def send(self, conn, msg):
        encodedMsg = msg.encode(self.FORMAT)
        msgLength = str(len(encodedMsg)).encode(self.FORMAT)
        if len(msgLength) < self.HEADER:
            msgLength += b' ' * (self.HEADER - len(msgLength))

        # header
        conn.send(msgLength)

        # actual message
        conn.send(encodedMsg)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((self.host, self.port))
            except ConnectionRefusedError:
                print('Server down...')
                return

            client.settimeout(5)

            threading.Thread(target=self.recieve, args=(client, )).start()
            while True:
                msg = input()
                if not msg.strip():
                    continue

                self.send(client, msg)
                if msg == self.TERMINATE:
                    self.die.set()
                    client.close()
                    return

    def recieve(self, conn):
        while not self.die.is_set():
            try:
                header = conn.recv(self.HEADER)
            except OSError:
                # timeout error
                continue
            if not header:
                # if the message is blank, continue
                continue
            msgLength = int(header)
            msg = conn.recv(msgLength)

            print(msg.decode(self.FORMAT))


if __name__ == '__main__':
    host = '192.168.1.253'
    port = 9002

    client = Client(host, port)
    client.start()
