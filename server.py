import pickle, select, socket, asyncore

outgoing   =   []
paints     =   []

class MainServer(asyncore.dispatcher):
  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('', port))
    # print('Host name: ' + socket.gethostname())
    self.listen(10)
    
  def handle_accept(self):
    conn, addr = self.accept()
    print ('Connection address:' + addr[0] + " " + str(addr[1]))
    outgoing.append(conn)
    # conn.send(pickle.dumps(['id update', playerid]))
    SecondaryServer(conn)

class SecondaryServer(asyncore.dispatcher_with_send):
  def handle_read(self):
    global paints, outgoing
    try:
        res = self.recv(4096)
        if res:
            cmd = pickle.loads(res)
            if cmd[0] == 'up':
                paints.append(cmd[1])
                print('Received. up; ' + str(len(paints)))
            elif cmd[0] == 'ask':
                if cmd[1] < len(paints):
                    for player in outgoing:
                        player.send(pickle.dumps([cmd[1], paints[cmd[1]]]))
                print('Received. ask; n: ' + str(cmd[1]))

    except:
        pass


MainServer(4321)
asyncore.loop()