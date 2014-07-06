---
layout: default
title: 机器学习实践：Logistic Regression的应用
meta: Logistic Regression, machine learning
---
# {{ page.title }}
*{{ page.date | date_to_string }}*   

###背景知识(回归，优化，预测)
回归的作用是根据已知的信息对连续性的未知值作预测（比如今年某个商品的价格之类的），分为线性回归和非线性回归。线性回归概念很简单，举个例子。假如某个饮料点有过去7天某款饮料的销售记录，还有过去7天的天气（晴朗/阴天/下雨）以及气温。我们假设销量Y和天气X1以及气温X2存在线性相关的关系：\\(Y＝X\_{1}+X\_{2}\\)   
when \\(a \ne 0\\), then \\(ax\^2+c=0\\). but $$x={-b \pm \sqrt{b\^2-4a} \over 2a}.$$
