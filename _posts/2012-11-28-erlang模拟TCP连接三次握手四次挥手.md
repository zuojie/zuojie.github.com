---
layout: default
title: 你好，世界
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
