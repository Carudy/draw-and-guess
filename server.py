import pickle, socket, asyncore, random, time, re
from collections import defaultdict as dd 

port       =   5659
buff_size  =   4096

class God():
    def __init__(self):
        self.S = Main_server(port)
        self.clients    =   dd()
        self.paints     =   []
        self.n_player   =   0
        self.drawer     =   0
        self.poses      =   [-1] * 5
        self.names      =   dd(str)
        self.tps        =   dd(int)
        self.coins      =   dd(int)
        self.status     =   0 # 1: playing
        self.readys     =   dd(int)
        print('Sever started.')

        self.questions  =   [c for c in  re.split('[, \t]', open('cy', encoding='utf-8').read()) if len(c)]
        
    def send_paint(self, uid, x):
        if self.clients[uid]._closed: return
        if x < len(self.paints): 
            y = min(len(self.paints)-1, x + 60)
            data = ['draw', x, y] + self.paints[x:y+1]
            self.clients[uid].send(pickle.dumps(data))

    def find_display_place(self):
        for i in range(5):
            if self.poses[i]==-1 or self.clients[self.poses[i]]._closed:
                self.poses[i] = self.n_player
                return i
        return -1

    def set_name(self, x, y):
        self.names[x] = y

    def add_player(self, conn):
        self.n_player += 1
        tp = 1
        if self.drawer==0 or self.clients[self.drawer]._closed:
            tp = 0 
            self.drawer = self.n_player
        
        dp = self.find_display_place()
        if dp==-1:
            conn.send(pickle.dumps(['full']))
            return

        self.coins[self.n_player] = 0
        self.tps[self.n_player]   = 1
        conn.send(pickle.dumps(['reg', G.n_player, dp]))
        G.clients[G.n_player] = conn
        print ('New player: id:%d  display pos:%d' % (G.n_player, dp))

    def clean(self):
        for i in self.clients:
            if self.clients[i]._closed:
                self.names[i] = ''
                for j in range(5):
                    if self.poses[j]==i:
                        self.poses[j] = -1
                        break

    def send_user_info(self, uid):
        res = ['user']
        for i in range(5):
            if self.poses[i]!=-1:
                nm = self.names[self.poses[i]]
                tp = '画家' if self.tps[self.poses[i]]==0 else '猜测者'
                cn = '得分： {}'.format(self.coins[self.poses[i]])
                res.append((nm, tp, cn))
            else:
                res.append(('Empty', '', ''))
        self.clients[uid].send(pickle.dumps(res))

    def player_ready(self, uid):
        if self.status==1: return
        self.readys[uid] = 1
        self.clean()
        n = c = 0
        for u in self.clients:
            n += 1
            if self.readys[u]==1: c += 1
        print(n, c)
        if n>1 and n==c:
            self.start_game()

    def start_game(self):
        players = [u for u in self.clients if not self.clients[u]._closed]
        self.painter = random.choice(players)
        for u in players:
            if u==self.painter:
                self.answer = random.choice(self.questions)
                print(self.answer)
                self.clients[u].send(pickle.dumps(['info', 0, '你是画家']))
                time.sleep(0.05)
                self.clients[u].send(pickle.dumps(['info', 1, '题目：{}'.format(self.answer)]))
                time.sleep(0.05)
                self.clients[u].send(pickle.dumps(['tp', 0]))
                self.tps[u] = 0
            else:
                self.clients[u].send(pickle.dumps(['info', 0, '你是猜测者']))
                time.sleep(0.05)
                self.clients[u].send(pickle.dumps(['info', 1, '猜一个成语']))
        self.status = 1

    def redraw(self, uid):
        if self.tps[uid]!=0: return
        self.paints     =   []
        self.broadcast(['redraw'])

    def broadcast(self, data):
        data = pickle.dumps(data)
        for u in self.clients:
            if not self.clients[u]._closed:
                self.clients[u].send(data)
                time.sleep(0.05)

    def stop_game(self):
        self.status = 0
        self.clients[self.painter].send(pickle.dumps(['tp', 1]))
        time.sleep(0.05)
        self.painter = -1
        self.clean()
        for u in self.clients:
            self.readys[u] = 0

    def deal_ans(self, uid, ans):
        if self.status!=1: return
        if ans!=self.answer:
            print('Wrong answer!')
            self.clients[uid].send(pickle.dumps(['info', 0, '猜错了']))
            self.coins[uid] -= 1
        else:
            print('Right answer!')
            self.redraw(self.painter)
            self.coins[self.painter] += 1
            self.coins[uid] += 1
            self.broadcast(['info', 0, '{} 猜对了！'.format(self.names[uid])])
            time.sleep(0.05)
            self.stop_game()


class Main_server(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)
    
    def handle_accept(self):
        conn, addr = self.accept()
        print ('Connection address:' + addr[0] + " " + str(addr[1]))
        G.add_player(conn)
        Handler(conn)


class Handler(asyncore.dispatcher_with_send):
    def handle_read(self):
        try:
            res = self.recv(buff_size)
            if res:
                cmd = pickle.loads(res)
                if cmd[0] == 'up':
                    G.paints.append(cmd[2])
                elif cmd[0] == 'ask':
                    G.send_paint(cmd[1], cmd[2])
                elif cmd[0] == 'name':
                    G.set_name(cmd[1], cmd[2])
                elif cmd[0] == 'user':
                    G.send_user_info(cmd[1])
                elif cmd[0] == 'play':
                    G.player_ready(cmd[1])
                elif cmd[0] == 'redraw':
                    G.redraw(cmd[1])
                elif cmd[0] == 'ans':
                    G.deal_ans(cmd[1], cmd[2])

        except Exception as e:
            print(e)


G = God()
asyncore.loop()