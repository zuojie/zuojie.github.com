---
layout: default
title: ErlangMapReduceFramework实现小记 
---
# {{ page.title }}   
*{{ page.date | date_to_string}}*   
之前学习Erlang时实现过一个粗糙的Erlang分布式计算系统[EDCFP](https://github.com/zuojie/EDCFP)，因为Erlang天然的分布式特性支持，以及异构机器之间互调函数的极大便利性，所以做这种事情一(hao)点(wu)都(ke)不(ji)费(han)事(liang)。现在回头看EDCFP，真是too young too simple，it's totally naive。于是花点心思重构了一下，以期普适性有所增强。   
###一，核心思想
仍然是pmap的思想，即在map中新建进程，大家分头行动。如果在同一台机器上，模型类似多进程编程；如果是在多台机器上，就是分布式计算了。但是对erlang来说，二者并无太大差别，所以用erlang写分布式程序跟用传统语言写多进程程序感觉是差不多的。要说差别,就是比传统语言的多进程编程模型还要简洁，要考虑的杂事更少了，比如互斥锁什么的，因为erlang中不同进程之间的交互是通过异步消息传输进行的，而非共享内存。所以很少存在竞争资源的情况。   
这个framework的分布式架构模仿Hadoop，采用Master-Slave的主从结构，不同的是Master同样参与计算。节点之间的安全通信就交给erlang虚拟机来解决啦，我们只需要在不同节点的home目录下放置一个内容相同的cookie文件即可。考虑到分布式计算作业中不同节点之间的相互影响很小，因为即使某个节点的进程挂掉了，打个log等master善后处理即可(不过，让人呵呵的是这个framework中log模块还没有加,所以这还只是一个坑:()，不需要其他节点都停下来。所以新建进程使用spawn，而不是spawn_link。重构后的系统支持本地模式(即只调用Master节点进行计算)和分布式模式。   
###二，更新内容
本系统的历史故事请移步[这里](https://github.com/zuojie/EDCFP),这次重构主要集中在增加使用的灵活性和健壮性方面。变动主要在mprd_master.erl文件，新增修改内容包括:   

* 支持单机模式调用, 即只使用master进行计算
* 需要用户指定map函数用于进行作业计算，和reduce函数用于进行汇总结果的处理，更像hadoop了LOL
* 列表拆分工作由ErlangMapReduceFramework来完成，即根据参与计算的节点数量来平均分配列表，用户只需传递进一个完整列表即可

###三，用法示例
由于系统很不成熟，用法并不像Hadoop那样有严格的规范流程，看到大跌眼镜之处请默默谅解。   
首先以一个简单示例入手，还是那个求阶乘的栗子（当然你可以换成斐波那契数列，乘方等）。这个例子是按照ErlangMapReduceFramework的标准用法来的。首先编写用户函数:
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
我们使用my_map进行阶乘的计算，使用my_reduce对最终结果进行处理，这里我们采取直接输出的处理方式 。   
看一下master节点的代码:
<pre class="prettyprint lang-erl">
-module(mprd_master).                                                           
-compile(export_all).                                                           
map(Func, UserReduce, List, SlaveNum) ->                                           
    Pid = self(),                                                                  
    Pids = lists:map(fun(I) -> spawn(fun() -> do_work(Pid, Func, I) end) end, List),
    case SlaveNum > 0 of                                                           
        true -> Res = gather(Pids, SlaveNum);                                      
        _ -> Res = Pids                                                            
    end,                                                                           
    R = reduce(Res),                                                               
    case whereis(master) of                                                        
        undefined ->                                                               
            ok;                                                                    
        _ ->                                                                       
            unregister(master)                                                     
    end,                                                                           
    UserReduce(R).
reduce([]) ->                                                                   
    [];                                                                         
reduce([H | T]) ->                                                              
    receive                                                                     
        {H, Res} ->                                                             
            [Res | reduce(T)]                                                   
    end.                                                                        
gather(Pids, 0) ->                                                              
    Pids;                                                                       
gather(Pids, SlaveNum) ->                                                          
    receive                                                                        
        {finished, SlaveRes} ->                                                    
            Res = lists:append(Pids, SlaveRes),                                    
            gather(Res, SlaveNum - 1)                                              
    end.                                                                           
print(Ele) ->                                                                      
    io:format("~w~n", [Ele]).                                                      
do_work(Parent, Func, I) ->                                                        
    Parent ! {self(), (catch Func(I))}.                                            
my_spawn({SlaveNode, L}, Func) ->                                                  
    spawn(SlaveNode, mprd_slave, map, [Func, L, master, node()]).                  
my_split([], _, _, L) ->                                                           
    L;                                         
my_split(List, Len, NodeCnt, L) when length(List) >= Len ->                        
    case length(L) of                                                              
        NodeCnt  ->                                                                
            [List | L];                                                            
        _ ->                                                                    
            {H, T} = lists:split(Len, List),                                    
            my_split(T, Len, NodeCnt, [H | L])                                  
    end;                                                                        
my_split(List, Len, _, L) ->                                                    
    L.                                                                          
start(Func, UserReduce, L) ->                                                   
    %spawn(mprd_master, map, [Func, UserReduce, L, 0]).                         
    map(Func, UserReduce, L, 0).                     
start(SlaveNodes, Func, UserReduce, L) when length(SlaveNodes) > length(L) -1 ->
    io:format("Make sure the number of slave node is less than the length of List please!\n");
start(SlaveNodes, Func, UserReduce, L) ->                                       
    % slave + master                                                            
    Nodes = length(SlaveNodes) + 1,                                             
    Len = length(L) div Nodes,                                                  
    [H | Lists] = my_split(L, Len, length(SlaveNodes), []),                     
    io:format("Master: ~w~n", [H]),                                             
    XS = lists:zip(SlaveNodes, Lists),                                          
    io:format("~p~n", [XS]),                                                    
    register(master, spawn(mprd_master, map, [Func, UserReduce, H, length(SlaveNodes)])),
    [my_spawn(X, Func) || X <- XS],                                             
    ok.
</pre>
slave节点代码：
<pre class="prettyprint lang-erl">
-module(mprd_slave).                                                               
-compile(export_all).                                                              
map(Func, List, MasterName, MasterNode) ->                                         
    Pids = lists:map(fun(I) -> spawn(fun() -> do_work(MasterName, MasterNode, Func, I) end) end, List),
    {MasterName, MasterNode} ! {finished, Pids}.                                   
do_work(MasterName, MasterNode, Func, I) ->                                        
    {MasterName, MasterNode} ! {self(), (catch Func(I))}.
</pre>
用法如下：    
1,环境准备，生成输入数据   
这次使用的是3台slave + 1台master的架构，环境都是Centos X64, erlang版本为：   
Erlang R16B02 (erts-5.10.3) [source] [64-bit] [smp:16:16] [async-threads:10] [hipe] [kernel-poll:false]   
节点名称分别为master，qb2，qb3，qb4   
输入数据：   
![input](http://zuojie.github.io/demo/erlang_1.png)   
2,调用master函数，将用户函数和输入数据传入   
首先是单机版:   
<pre class="prettyprint lang-erl">

(master@QBHadoop1)4> mprd_master:start(fun(X) -> factorial:my_map(X) end, fun(X) -> factorial:my_reduce(X) end, L).   

</pre>
输出:   
[1,2,6,24,120,720,5040,40320,362880,3628800,39916800,479001600,   
6227020800,87178291200,1307674368000,20922789888000,355687428096000,   
6402373705728000,121645100408832000,2432902008176640000]   
![output](http://zuojie.github.io/demo/erlang_2.png)   
然后是集群版:   
<pre class="prettyprint lang-erl">
(master@QBHadoop1)2> Slaves=[qb2@QBHadoop2, qb3@QBHadoop3, qb4@QBHadoop4].   
(master@QBHadoop1)4> mprd_master:start(Slaves, fun(X) -> factorial:my_map(X) end, fun(X) -> factorial:my_reduce(X) end, L).
</pre>
输出：   
[20922789888000,355687428096000,6402373705728000,121645100408832000,   
2432902008176640000,39916800,479001600,6227020800,   
87178291200,1307674368000,720,5040,40320,362880,3628800,1,2,6,24,120]   
![output](http://zuojie.github.io/demo/erlang_3.png)   
图中红色圈出的是为每个节点分配的list。由于各个节点计算完毕的时间不同，因此结果列表和输入列表顺序是不一致的。

下面再来看一个非常规用法的示例:快速排序的并行版本。   
单进程版的快排erlang代码[这里](https://github.com/zuojie/CodeBase/blob/master/Awesome_Erlang_Snippets.md)有。并行版本代码如下:
<pre class="prettyprint lang-erl">
-module(qsort).                                                                    
-compile(export_all).                                                              
my_reduce([]) ->                                                                   
    [];                                                                            
my_reduce(OutDat) ->                                                               
    OutDat.                                                                        
qsort([]) -> [];                                                                   
qsort([Pivot]) -> [Pivot];                                                         
qsort([Pivot | Rest]) ->                                                           
    L = [X || X <- Rest, X =< Pivot],                                              
    R = [X || X <- Rest, X > Pivot],                                               
    [SortL, SortR] = mprd_master:start(fun qsort/1, fun my_reduce/1, [L, R]),   
    SortL ++ [Pivot] ++ SortR.
</pre>
输出：   
![output](http://zuojie.github.io/demo/erlang_4.png)   

注意，这里的并行只是单机多进程模式，而非分布式模式。因为排序时列表拆分需要保证列表之间有序，所以列表的自动拆分对排序这种情况是不适用的。这也暴露了这个系统封装性做的还远远不够啊远远不够。同时，这里说的“非常规用法”是指我们在应用程序中调用了framework的入口函数，和传统用法中的直接调用framework的入口函数，然后把用户函数传递进去的方式不同,感觉很诡异吧～
###四，总结
Erlang内置的分布式支持，对用户极其友好的的节点通信认证机制等特性，非常适合用来做分布式程序的开发。尤其对于数据分布在多台业务机上的情形，可以考虑使用erlang来实现一些简单的并发数据统计的工作，而不需要先把数据拉到同一台处理机上再做处理了。

___

###项目地址
[https://github.com/zuojie/ErlangMapReduceFramework](https://github.com/zuojie/ErlangMapReduceFramework)
