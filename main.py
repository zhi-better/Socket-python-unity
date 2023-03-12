# 导入套接字模块
import socket
# 导入线程模块
import threading
# 定义个函数,使其专门重复处理客户的请求数据（也就是重复接受一个用户的消息并且重复回答，直到用户选择下线）
import time
import base64

g_connection_pool = []

def dispose_client_request(tcp_client_1, tcp_client_address):
    # 5 循环接收和发送数据
    while True:
        try:
            recv_data = tcp_client_1.recv(4096)
        except ConnectionResetError:
            print("client:{} has closed, it has been remove from the connection pool. ".format(tcp_client_address))
            tcp_client_1.close()
            g_connection_pool.remove(tcp_client_1)
            return
        # 6 有消息就回复数据，消息长度为 0 就是说明客户端下线了
        if recv_data:
            print("receive data from: {}, data are: {}".format(tcp_client_address, recv_data.decode()))
            send_data = "pong"
            tcp_client_1.send(send_data.encode())
            print("send data to: {}, data are: {}".format(tcp_client_address, send_data))
        else:
            print("client:{} has closed, it has been remove from the connection pool. ".format(tcp_client_address))
            tcp_client_1.close()
            g_connection_pool.remove(tcp_client_1)
            break

def scan_all_client():
    print('client scan thread start...')
    while True:
        for cli in g_connection_pool:
            try:
                cli.send("ping".encode())
            except ConnectionResetError:
                print("{} client has closed, it has been remove from the connection pool. ".format(cli))
                cli.close()
                g_connection_pool.remove(cli)
        time.sleep(5)
        print("start to check all client status, client count: {}".format(len(g_connection_pool)))

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 4444

    print('starting server...')
    # 1 创建服务端套接字对象
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置端口复用，使程序退出后端口马上释放
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    # 2 绑定端口
    tcp_server.bind((host, port))
    print('server port bind successfully, server host: {}, server port: {}...'.format(host, port))
    # 3 设置监听
    tcp_server.listen(128)
    print('start to listen connections from client...')
    # 开启客户端扫描线程
    # thd_scan = threading.Thread(target=scan_all_client)
    # thd_scan.start()
    # 4 循环等待客户端连接请求（也就是最多可以同时有128个用户连接到服务器进行通信）
    while True:
        tcp_client_1, tcp_client_address = tcp_server.accept()
        # 创建多线程对象
        thd = threading.Thread(target=dispose_client_request, args=(tcp_client_1, tcp_client_address))
        g_connection_pool.append(tcp_client_1)
        # 设置守护主线程  即如果主线程结束了 那子线程中也都销毁了  防止主线程无法退出
        # thd.setDaemon(True)
        # 启动子线程对象
        thd.start()
        print("new client connected, client address: {}, total client count: {}".format(tcp_client_address, len(g_connection_pool)))

    # 7 关闭服务器套接字 （其实可以不用关闭，因为服务器一直都需要运行）
    # tcp_server.close()
