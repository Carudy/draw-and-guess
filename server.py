import pickle, socket, asyncore

port       =   5659
buff_size  =   4096

class Main_server(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.clients =   []
        self.paints  =   []
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)
    
    def handle_accept(self):
        self.clients = [client for client in self.clients if not client._closed]
        conn, addr = self.accept()
        print ('Connection address:' + addr[0] + " " + str(addr[1]))
        self.clients.append(conn)
        Handler(conn)

    def send_paint(self, x):
        self.clients = [client for client in self.clients if not client._closed]
        for player in self.clients:
            player.send(pickle.dumps([x, self.paints[x]]))


class Handler(asyncore.dispatcher_with_send):
    def handle_read(self):
        try:
            res = self.recv(buff_size)
            if res:
                cmd = pickle.loads(res)
                if cmd[0] == 'up':
                    S.paints.append(cmd[1])
                    print('Received. up; ' + str(len(S.paints)))
                elif cmd[0] == 'ask':
                    if cmd[1] < len(S.paints): S.send_paint(cmd[1])
                    print('Received. ask; n: ' + str(cmd[1]))

        except Exception as e:
            print(e)


S = Main_server(port)
asyncore.loop()