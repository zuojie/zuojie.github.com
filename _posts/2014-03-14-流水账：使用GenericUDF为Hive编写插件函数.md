---
layout: default
title: 流水账：使用GenericUDF为Hive编写扩展函数 
meta: Hive, GenericUDF
---
# {{ page.title }}
*{{ page.date | date_to_string }}*

Hive官方没有提供GenericUDF的编写指导文档，官方维护的doc地址也经常变来变去导致google的不少链接404。比起Hadoop的javadoc，hive的有点敷衍了事，在上面找一些参考资料根本就get不到point。   
在官方没提供比较详细的GenericUDF编写指导前提下，我们还有一个比较好的方法，就是去[hive的源码](https://github.com/apache/hive)里寻找答案。我们可以在github上hive项目下直接搜索GenericUDF，你会分别在：*hive/ql/src/java/org/apache/hadoop/hive/ql/udf/generic*和*hive/itests/util/src/main/java/org/apache/hadoop/hive/ql/udf/generic*下找到很多hive内置的很多对GenericUDF的实现，比如nvl啦，case when啦，if啦等等。其中后边的目录里是一些基础问题的指导，比如UDF里怎么获取外部传递过来的string之类的，前者是hive内置随官方Hive安装包外发的扩展函数，主打实战。按照你的GenericUDF功能需求寻找相应的实现参考一下即可。   
本文要点如下：   

* 编写GenericUDF一般流程简述 
* 如何向hive里添加扩展里引用的外部资源文件
* 中文乱码问题

本次实现基于**Hive-0.12.0**和**hadoop-1.2.1**。   

####动手写GenericUDF
这部分网上很多教程，这里主要说一些自己总结的点，实现自己的GUDF首先继承父类[GenericUDF](http://hive.apache.org/javadocs/r0.10.0/api/org/apache/hadoop/hive/ql/udf/generic/GenericUDF.html)，实现里边的3个方法即可：   
**initialize(ObjectInspector[] arguments)**   

* initialize函数需要注意一点是其返回值要和你的扩展函数最终返回值保持一致；另外用户输入参数的合法性检查主要
也是在这里进行

**evaluate(GenericUDF.DeferredObject[] arguments)**   

* 你的扩展函数逻辑主要在这里实现

**getDisplayString(String[] children)** 

* 里面写一些介绍性信息，在用户对sql语句进行explain的时候显示。我想你用膝盖也能想到这和@Description里的内容是在不同场合显示的，后者在用户使用desc function命令的时候显示函数介绍

代码以一个转换中文国家名为数字id的UDF为例，输入2个参数，第一个参数为国家名，第二个参数为假设国家名找不到输出的默认值。上码：  

```java
package com.arvinpeng.udf;
import java.util.Hashtable;
import java.util.Set;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileNotFoundException;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.hive.ql.exec.Description;
import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.exec.UDFArgumentLengthException;
import org.apache.hadoop.hive.ql.exec.UDFArgumentTypeException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDFUtils;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.StringObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;

/**
 * author: zuojiepeng
 * date: 2014/03/14
 * desc: 将用户输入的国家名转化为数字id表示
 */

@Description(
        name="loc 2 id",
        value="_FUNC_(string arg1, string arg2) - input two string",
        extended="return the id corresponding to arg1\n" +
        "Example:\n" +
        "> SELECT _FUNC_(\"中国\", \"12\") FROM dual;\n"
)

public class Loc2ID extends GenericUDF {
    private transient ObjectInspector[] argumentOIs;
    public static String cityf = "country2id.txt";
    public static final String SEP = "\\|";
    public static Hashtable<String, String> city2id = new Hashtable<String, String>();

    public void ReadFile(Hashtable<String, String> tbl, String fname) throws IOException {
        FileInputStream fis = new FileInputStream(fname);
        InputStreamReader isr = new InputStreamReader(fis, "utf-8");
        BufferedReader br = new BufferedReader(isr);
        String tp = null;
        String[] tmp = null;
        while((tp = br.readLine()) != null) {
            tp = tp.trim();
            tmp = tp.split(SEP);
            tbl.put(tmp[0], tmp[1]);
        }
    }

    @Override
    public ObjectInspector initialize(ObjectInspector[] args)
                            throws UDFArgumentException {
        if (args.length > 2) {
            throw new UDFArgumentLengthException(
                    "The operator 'loc2id' accepts at most 2 arguments.");
        }
        try {
            ReadFile(city2id, cityf);
        } catch (IOException e) {
        }
        argumentOIs = args;
        return PrimitiveObjectInspectorFactory.javaStringObjectInspector;
    }

    @Override
    public Object evaluate(DeferredObject[] args) throws HiveException {

        Object base = args[0].get();
        Object power = args[1].get();
        StringObjectInspector soi0 = (StringObjectInspector)argumentOIs[0];
        StringObjectInspector soi1 = (StringObjectInspector)argumentOIs[1];
        String str_key = soi0.getPrimitiveJavaObject(base);
        String str_val = soi1.getPrimitiveJavaObject(power);
        String ret = city2id.get(str_key);
        if(ret == null) {
            return str_val;
        }
        return ret;
    }

    @Override
    public String getDisplayString(String[] args) {
        StringBuilder sb = new StringBuilder();
        sb.append("convert country ");
        sb.append(args[0]);
        sb.append(" to relevant ID, if ");
        sb.append(args[0]);
        sb.append(" is null ");
        sb.append("returns");
        sb.append(args[1]);
        return sb.toString() ;
    }
}

```

编译打包添加到hive里的整个流程如下：

* 1、javac -cp /data/home/hadoop/hadoop-core-1.2.1.jar:/data/home/hive-0.12.0/lib/hive-serde-*.jar:/data/home/hive-0.12.0/lib/hive-exec-0.12.0.jar Loc2ID.java -d . -encoding utf8 
* 2、jar cvf Loc2ID.jar com/arvinpeng/udf/Loc2ID.class
* 3、add jar /data/home/hive-0.12.0/lib/hive-serde-0.12.0.jar;
* 4、add jar  /data/home/hadoop/hadoop-core-1.2.1.jar;
* 5、add jar /data/home/hive-0.12.0/lib/hive-exec-0.12.0.jar ;
* 6、add file /data/mr/country2id.txt;
* 7、add jar /data/qb/mr/Loc2ID.jar;
* 8、create temporary function arvin_loc as 'com.arvinpeng.udf.Loc2ID';            

我这边的hive编码环境是gbk，其中1编译时由于代码文件中含有中文，所以编译时指定-encoding选项，否则报警告；3、4、5步非必需执行；6就是添加外部引用资源的方式，我的扩展里需要读取country2id文件中的内容，目测添加到hive之后你的jar包和资源文件在同一个目录，所以之后代码里直接使用相对路径即可；8便是注册函数名；注意，每次更新你自己的jar文件后只需重新执行7即可使更新生效。所有这些完成后就可以测试了：   
hive>select arvin_loc('中国', '-1') from dual;   
-1   
出现问题，我的文件里肯定是有中国对应的数字id的，但是函数却没找到，经过排查，发现我的hive环境是gbk编码，所以读入时编码出错，导致hashtable里存的是乱码，自然就找不到“中国”对应的id了。强行指定java按照utf8编码读入文件即可（处理方式参考上面代码），另外推荐一个对java中文乱码比较好的解释[java字符编码原理浅析](http://blog.csdn.net/abing37/article/details/5571963)再次尝试：   
hive>select arvin_loc('中国', '-1') from dual;   
86     

流水账毕。


