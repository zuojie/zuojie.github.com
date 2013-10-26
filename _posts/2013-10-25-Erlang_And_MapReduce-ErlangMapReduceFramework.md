---
layout: default
title: ErlangAndMapReduceErlangMapReduceFramework 
---
# {{ page.title }}   
*{{ page.date | date_to_string}}*   
之前学习Erlang时实现过一个粗糙的Erlang分布式计算系统[EDCFP](https://github.com/zuojie/EDCFP)，因为Erlang天然的分布式特性支持，以及异构机器之间互调函数的极大便利性，所以做这种事情一(hao)点(wu)都(ke)不(ji)费(han)事(liang)。现在回头看EDCFP，真是too young too simple，it's totally naive。于是花点心思重构了一下，以期适用性有所增强。   
###一，核心思想
仍然是pmap的思想，即在map中新建进程，大家分头行动。如果在同一台机器上，模型类似多进程编程；如果是在多台机器上，就是分布式计算了。但是对erlang来说，二者并无太大差别，所以用erlang写分布式程序跟用传统语言写多进程程序感觉是差不多的。要说差别,就是比传统语言的多进程编程模型还要简洁，要考虑的杂事更少了，比如互斥锁什么的。   
还有就是分布式架构同Hadoop，采用Master-Slave的主从结构，不同的是Master同样参与计算。节点之间的安全通信就交给erlang虚拟机解决啦，考虑到分布式计算节点之间影响很小，即使某个节点的进程挂掉了，打个log等master善后即可(当然，值得呵呵的是log模块还没有加,所以这还只是一个坑:[])，不需要大家都停下来围观。所以新建进程使用spawn，而不是spawn_link。重构后的系统支持只调用Master进行计算，即本地模式。   
###二，更新内容
本系统的历史故事请移步[这里](https://github.com/zuojie/EDCFP),这次重构主要集中在使用的灵活性和健壮性方面。变动主要集中在mprd_master.erl文件，新增修改内容包括:   

* 支持单机模式调用, 即只使用master进行计算
* 需要用户指定map函数用于进行作业计算，和reduce函数用于进行汇总结果的处理，更像hadoop了LOL
* 列表拆分工作由ErlangMapReduceFramework来完成，即根据参与计算的节点数量来平均分配列表，用户只需传递进一个完整列表即可
###三，用法示例
由于系统很不成熟，用法并不像Hadoop那样有严格的规范流程，看到大跌眼镜之处请默默谅解。首先以一个简单示例入手，还是那个求斐波那契的栗子（当然你可以换成阶乘，乘方等）。这个例子是按照ErlangMapReduceFramework的标准用法来的。首先编写用户函数:
<pre class="prettyprint lang-erl">
-module(factorial).                                                                
-export([my_map/1, my_reduce/1]).                                                  
                                                                                   
fact(0) -> 1;                                                                      
                                                                                   
fact(N) when N < 0 -> io:format("参数错误~n");                                     
                                                                                   
fact(N) when N > 0 -> N * fact(N - 1).                                             
                                                                                   
% used at all nodes                                                                
my_map(InDat) ->                                                                   
    fact(InDat).                                                                   
                                                                                   
% used only at master side                                                         
my_reduce([]) ->                                                                   
    [];                                                                            
                                                                                   
my_reduce(OutDat) ->                                                               
    io:format("my reduce come in~n", []),                                          
    io:format("~w~n", [OutDat]). 
</pre>
