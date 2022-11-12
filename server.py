import socket
import threading
class Server(object):
    def __init__(self) -> None:
        self.server=None
        self.init_client()
        self.centerx=None
        self.centery=None
        self.move=False
        self.catch=False
        self.out=False
    def init_client(self):
        host = "192.168.1.62"  # 设置IP
        port = 5500  # 设置端口号
        tcpserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP/IP套接字
        tcpserver.bind((host, port))  # 绑定地址（host, port）到套接字
        tcpserver.listen(5)  # 设置最多连接数量
        print("等待客户端连接...")
        self.server=tcpserver
    def str_to_bool(self,str):
        # print(str.lower(),type(str))
        if str.lower() == 'true':
            print(1)
            return True  
        else:
            print(2)
            return False
    def SingleReceiveText(self):
        """
        单次接收发送文字
        """
        # host = socket.gethostname()  # 获取主机地址  socket.gethostname()

        tcpclient, addr = self.server.accept()  # 被动接收TCP客户端连接
        print("客户端已经连接")
        while True:
            info = tcpclient.recv(1024).decode()  # 接收客户端数据
            new_info=info[1:-1]
            new_info=[int(i)if idx<=3 else i for idx,i in enumerate(new_info.split(','))]
            # print("接收到的内容：", new_info)
            send_data = "success"
            tcpclient.send(send_data.encode())  # 发送TCP数据
            self.centerx=(int(new_info[2])+int(new_info[0]))//2
            self.centery=(int(new_info[3])+int(new_info[1]))//2
            if len(new_info)==7:
                print(new_info[4],type(new_info[4]))
                print(new_info[5],type(new_info[5]))
                print(new_info[6],type(new_info[6]))
                if new_info[4]==" true":self.move=True
                else:self.move=False
                if new_info[5]==" true":self.catch=True
                else:self.catch=False
                if new_info[6]==" true":self.out=True
                else:self.out=False
            print("接收到的内容：", new_info)
            # print(self.move,self.catch,self.out)
        # tcpclient.close()
        # self.server.close()
if __name__=="__main__":
    myserver=Server()
    t1=threading.Thread(target=myserver.SingleReceiveText)
    t1.start()