---
layout: default
title: 流水账：Suse下安装Storm-单机和集群模式 
meta: Storm,linux 
---
# {{ page.title }}
*{{ page.date | date_to_string }}*

#1. 安装单机版   
Storm的依赖软件比较多，需要装Python、zookeeper、zeromq以及jzmq，然后才是storm的安装。   
###1.1 安装Python2.7.x   
* 编译安装过程略    
###1.2 安装java, jdk 1.6.x   
* 解压tar包即可使用，更高版本的jdk未测试，应该也可以。   
以下bashrc中的java，zookeeper等bin路径均用ln -s做了软链，主路径不再带版本号，如下：
* 在~/.bashrc中追加：   
 ***export JAVA_HOME="/home/arvinpeng/proj/jdk"***   
 ***export PATH=$JAVA_HOME/bin:$PATH:/sbin***   
* 然后执行source命令    
 ***source ~/.bashrc***
###1.3 安装Zookeeper3.4.6
* 解压tar包即可使用，更高的版本应该也兼容   
* 在~/.bashrc追加：   
 ***export ZK_HOME="/home/arvinpeng/proj/zookeeper"***    
 ***export PATH=$JAVA_HOME/bin:$ZK_HOME/bin:$PATH:/sbin***
* cp zookeeper/conf/zoo_sample.cfg zookeeper/conf/zoo.cfg (用zoo_sample.cfg制作$ZOOKEEPER_HOME/conf/zoo.cfg)


