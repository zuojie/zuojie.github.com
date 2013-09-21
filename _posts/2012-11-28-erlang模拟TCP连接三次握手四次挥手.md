---
layout: default
title: Erlang模拟TCP连接三次握手四次挥手
---
# Erlang模拟TCP连接三次握手四次挥手
*{{ page.date | date_to_string }}*   
TCP连接的断开和建立是it从业者尤其是面试官喜闻乐见的内容，今天笔者来借助erlang模拟一下TCP建立过程的三次握手（Three-way Handshak）和断开的四次挥手（Four-way handshake）过程，之所以选择erlang，是因为最近在看erlang的东西。   

三次握手的目的是连接服务器指定端口，建立TCP连接,并同步连接双方的序列号和确认号并交换 TCP 窗口大小信息.在socket编程中，客户端执行connect()时。将触发三次握手。   

三次握手：   
第一次握手 ->   
client发送一个TCP的syn置为1的包，指明client打算连接的server的端口，和自己的初始序列号(Seq Number)，这个序列号保存在包头的Sequence Number字段里。此时client处于SYN_SENT状态，server处于LISTEN状态。   
第二次握手 ->   
server发回确认包（ack应答），syn和ack均置为1，同时将确认序号（Ack Number）设置为client的序列号加1。此时server处于SYN_RCVD状态。   
第三次握手 ->   
client发送确认包（ack确认），ack置为1。并把server发过来的Seq number加1作为此次发送的Ack Number。此时client处于ESTABLISHED状态，server收到最后一次的ack确认后也处于ESTABLISHED状态。   
完成三次握手后，TCP连接建立，开始传输数据。   
盗图总结：   
![p1](http://zuojie.github.io/article/erlang_tcp_p1.jpg)   
TCP连接的断开需要发送四次包，因为TCP的连接时全双工的。每一端的关闭都需要主动发起一次fin报文段告知对方自己已经没有数据流流给对方，这条单向的TCP连接可以断开了，而对方则需要回应一个ack确认，来确认关闭这条连接。所以两边都关闭总共需要发送4次TCP报文。client和server哪个首先发起断开请求是不一定的，在socket编程中，任何一方调用close()就会触发挥手操作。   
四次挥手：（假设server端首先传输完数据，发起断开连接请求）   
第一次挥手 ->   
server发送一个fin报文给client，fin字段置为1。发送完毕server进入FIN_WAIT_1状态。   
第二次挥手 ->   
client收到fin报文段，回送一个确认包（ack确认），ack置为1，ack报文的的Seq Number为server发送来的Ack Number，Ack Number为server发送来的Seq Number加1。此时client处于CLOSE_WAIT状态。   
第三次挥手 ->   
经过若干时间，client也没有数据流要流向server了，于是向server发起一个fin报文，fin字段置为1，Seq Number和Ack Number和刚才向server发送的ack报文一致。此时client处于LAST_ACK状态。   
第四次握手 ->   
server发回ack确认报文，ack置为1，Seq Number为server向client发fin报文段时的Seq Number + 1，Ack Number为client发来的Seq Number + 1.此时Server处于TIME_WAIT状态。经过2MSL后，不出意外的话，server进入CLOSED态。   

盗图总结：   
![p1](http://zuojie.github.io/article/erlang_tcp_p2.jpg)   
下面是对上文中出现的几个状态的解释：   
CLOSED: 这个没什么好说的，表示初始状态。   
LISTEN: 这个也是非常容易理解的一个状态，表示服务器端的某个SOCKET处于监听状态，可以接受连接了。   
SYN_RCVD: 这个状态表示接受到了SYN报文，在正常情况下，这个状态是服务器端的SOCKET在建立TCP连接时的三次握手会话过程中的一个中间状态，很短暂，基本上用netstat你是很难看到这种状态的，除非你特意写了一个客户端测试程序，故意将三次TCP握手过程中最后一个ACK报文不予发送。因此这种状态时，当收到客户端的ACK报文后，它会进入到ESTABLISHED状态。   
SYN_SENT: 这个状态与SYN_RCVD遥想呼应，当客户端SOCKET执行CONNECT连接时，它首先发送SYN报文，因此也随即它会进入到了SYN_SENT状态，并等待服务端的发送三次握手中的第2个报文。SYN_SENT状态表示客户端已发送SYN报文。   
ESTABLISHED：这个容易理解了，表示连接已经建立了。   
FIN_WAIT_1: 这个状态要好好解释一下，其实FIN_WAIT_1和FIN_WAIT_2状态的真正含义都是表示等待对方的FIN报文。而这两种状态的区别是：   

FIN_WAIT_1状态实际上是当SOCKET在ESTABLISHED状态时，它想主动关闭连接，向对方发送了FIN报文，此时该SOCKET即进入到FIN_WAIT_1状态。而当对方回应ACK报文后，则进入到FIN_WAIT_2状态，当然在实际的正常情况下，无论对方何种情况下，都应该马上回应ACK报文，所以FIN_WAIT_1状态一般是比较难见到的，而FIN_WAIT_2状态还有时常常可以用netstat看到。   
FIN_WAIT_2：上面已经详细解释了这种状态，实际上FIN_WAIT_2状态下的SOCKET，表示半连接，也即有一方要求close连接，但另外还告诉对方，我暂时还有点数据需要传送给你，稍后再关闭连接。   
TIME_WAIT: 表示收到了对方的FIN报文，并发送出了ACK报文，就等2MSL后即可回到CLOSED可用状态了。如果FIN_WAIT_1状态下，收到了对方同时带FIN标志和ACK标志的报文时，可以直接进入到TIME_WAIT状态，而无须经过FIN_WAIT_2状态。   
CLOSING: 这种状态比较特殊，实际情况中应该是很少见，属于一种比较罕见的例外状态。正常情况下，当你发送FIN报文后，按理来说是应该先收到（或同时收到）对方的ACK报文，再收到对方的FIN报文。但是CLOSING状态表示你发送FIN报文后，并没有收到对方的ACK报文，反而却也收到了对方的FIN报文。什么情况下会出现此种情况呢？其实细想一下，也不难得出结论：那就是如果双方几乎在同时close一个SOCKET的话，那么就出现了双方同时发送FIN报文的情况，也即会出现CLOSING状态，表示双方都正在关闭SOCKET连接。   
CLOSE_WAIT: 这种状态的含义其实是表示在等待关闭。怎么理解呢？当对方close一个SOCKET后发送FIN报文给自己，你系统毫无疑问地会回应一个ACK报文给对方，此时则进入到CLOSE_WAIT状态。接下来呢，实际上你真正需要考虑的事情是察看你是否还有数据发送给对方，如果没有的话，那么你也就可以close这个SOCKET，发送FIN报文给对方，也即关闭连接。所以你在CLOSE_WAIT状态下，需要完成的事情是等待你去关闭连接。   
LAST_ACK: 这个状态还是比较容易好理解的，它是被动关闭一方在发送FIN报文后，最后等待对方的ACK报文。当收到ACK报文后，也即可以进入到CLOSED可用状态了。   
附上[erlang模拟TCP握手挥手](https://github.com/zuojie/zuojie.github.com/blob/master/demo/erlang_tcp_simulate.md)过程，其中没有进行错误处理：   
结果附图:   
![p1](http://zuojie.github.io/article/erlang_tcp_p3.jpg)   
附1：   
SYN攻击   
   在三次握手过程中，服务器发送SYN-ACK之后，收到客户端的ACK之前的TCP连接称为半连接(half-open connect).此时服务器处于Syn_RECV状态.当收到ACK后，服务器转入ESTABLISHED状态.   
     Syn攻击就是 攻击客户端 在短时间内伪造大量不存在的IP地址，向服务器不断地发送syn包，服务器回复确认包，并等待客户的确认，由于源地址是不存在的，服务器需要不断的重发直 至超时，这些伪造的SYN包将长时间占用未连接队列，正常的SYN请求被丢弃，目标系统运行缓慢，严重者引起网络堵塞甚至系统瘫痪。   
	  Syn攻击是一个典型的DDOS攻击。检测SYN攻击非常的方便，当你在服务器上看到大量的半连接状态时，特别是源IP地址是随机的，基本上可以断定这是一次SYN攻击.在Linux下可以如下命令检测是否被Syn攻击   
	  netstat -n -p TCP | grep SYN_RECV   
	  一般较新的TCP/IP协议栈都对这一过程进行修正来防范Syn攻击，修改tcp协议实现。主要方法有SynAttackProtect保护机制、SYN cookies技术、增加最大半连接和缩短超时时间等.   
	  但是不能完全防范syn攻击。   
	  附2：   
	  MSL是Maximum Segment Lifetime,译为“报文最大保留时刻”，他是任何报文在收集上存在的最长时刻，高出这个时刻报文将被丢弃。   
	  RFC 793中划定MSL为2分钟，现实应用中常用的是30秒，1分钟和2分钟等。2MSL即两倍的MSL，TCP的TIME_WAIT状态也称为2MSL守候状态，当TCP的一端提倡主动封锁，在发出最后一个ACK包后，即第3次握手完成后发送了第四次握手的ACK包后就进入了TIME_WAIT状态，必需在此状态上逗留两倍的MSL时刻。   
	   守候2MSL时刻首要目标是怕最后一个ACK包对方未收到，那么对方在超时后将重发第三次握手的FIN包，主动封锁端接到重发的FIN包后可以再发一个ACK应答包。在TIME_WAIT状态时两头的端口不能使用。   
