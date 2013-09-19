#!/user/bin/env python
#coding=gb2312

from django.db import models

# Create your models here.
class customerInfo(models.Model):
	goods_name = models.CharField(max_length=100)
	goods_book = models.BooleanField()
	min_price = models.IntegerField()
	phone = models.CharField(max_length=50)
	def __unicode__(self):
		return self.goods_name
		
class presentationerInfo(models.Model):
	phone = models.CharField(max_length=50)
	addr = models.CharField(max_length=20)
	def __unicode__(self):
		return self.addr
		
class habitInfo(models.Model):
	motto = models.CharField(max_length=100)
	task = models.CharField(max_length=100)
	nick = models.CharField(max_length=50)
	phone = models.CharField(max_length=50)
	day = models.IntegerField()
	hour = models.CharField(max_length=30)
	def __unicode__(self):
		return self.task
		
class participanterInfo(models.Model):
	name = models.CharField(max_length=50)
	nick = models.CharField(max_length=50)
	phone = models.CharField(max_length=50)
	ojs = models.CharField(max_length=100)
	def __unicode__(self):
		return self.ojs
		
class weatherReportInfo(models.Model):
	province = models.CharField(max_length=5)
	city = models.CharField(max_length=50)
	phone = models.CharField(max_length=50)
	name = models.CharField(max_length=50) #用于log记录
	def __unicode__(self):
		return self.city