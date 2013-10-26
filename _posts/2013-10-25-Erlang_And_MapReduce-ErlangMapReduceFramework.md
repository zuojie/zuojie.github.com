---
layout: default
title: ErlangMapReduceFramework实现小记 
---
# {{ page.title }}   
*{{ page.date | date_to_string}}*   
之前学习Erlang时实现过一个粗糙的Erlang分布式计算系统[EDCFP](https://github.com/zuojie/EDCFP)，因为Erlang天然的分布式特性支持，以及异构机器之间互调函数的极大便利性，所以做这种事情一(hao)点(wu)都(ke)不(ji)费(han)事(liang)。现在回头看EDCFP，真是too young too simple，it's totally naive。于是花点心思重构了一下，以期普适性有所增强。   
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
我们使用my_map进行阶乘的计算，使用my_reduce对最终结果进行处理，这里我们采取直接输出的做法。   
看一下master节点的代码:
<pre class="prettyprint lang-erl">
</pre>
slave节点代码：
<pre class="prettyprint lang-erl">
</pre>
用法如下：    
1,环境准备，生成输入数据   
这次使用的是3台slave + 1台master的架构，环境都是：   
Erlang R16B02 (erts-5.10.3) [source] [64-bit] [smp:16:16] [async-threads:10] [hipe] [kernel-poll:false]   
节点名称分别为master，qb2，qb3，qb4   
输入数据：
![input](http://zuojie.github.io/demo/erlang_1.png)
2,调用master函数，将用户函数和输入数据传入   
首先调用单机版:   
<pre class="prettyprint lang-erl">
(master@QBHadoop1)4> mprd_master:start(fun(X) -> factorial:my_map(X) end, fun(X) -> factorial:my_reduce(X) end, L).   
</pre>
输出:   
[1,2,6,24,120,720,5040,40320,362880,3628800,39916800,479001600,6227020800,87178291200,1307674368000,20922789888000,355687428096000,6402373705728000,121645100408832000,2432902008176640000]   
![output](http://zuojie.github.io/demo/erlang_2.png)   
然后调用集群版:   
<pre class="prettyprint lang-erl">
(master@QBHadoop1)4> mprd_master:start(fun(X) -> factorial:my_map(X) end, fun(X) -> factorial:my_reduce(X) end, L).   
</pre>

再来看一个非常规用法的示例，快速排序的并行版本。   
单机版的快排erlang代码[这里](https://github.com/zuojie/CodeBase/blob/master/Awesome_Erlang_Snippets.md)有。并行版本代码如下:
<pre class="prettyprint lang-erl">
</pre>
可见，其并没有按照求斐波那契数列的用户函数一样调用start入口函数，而是直接调用了framework里的map函数，究其原因是系统入口函数不能很好兼容快排作业的需求，所以快排作业只好取巧用了直接调用map的方式。这也暴露了这个系统封装性做的还远远不够啊远远不够。
###四，总结
Erlang内置的分布式支持，对用户及其友好的的节点认证机制等特性，非常适合用来做分不是程序的开发。尤其对于数据分布在多台业务机上的情形，可以考虑使用erlang来实现一些简单的数据统计的工作。
