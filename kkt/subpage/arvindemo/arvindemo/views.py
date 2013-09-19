#!/usr/bin/env python
#coding=gbk

from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
import datetime, string
from user_info.models import *
from django.template import Context, loader, RequestContext
import settings
	
def hello(request):
	return HttpResponse("hello girl")

def getTime(request):
	now = datetime.datetime.now()
	html = "<html>It is now %s<body></body></html>" % now
	return HttpResponse(html)
	
def hoursAhead(request, offset):
	try:
		offset = int(offset)
	except Http404:
		raise Http404()
	# assert False # for debug
	dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
	html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
	return HttpResponse(html)
	
def templateGetTime(request):
	current_date = datetime.datetime.now()
	return render_to_response('kktTemplate.html', locals())
	
def templateMall(request):
	return render_to_response('kktMall.html', locals()) 
	#html文件包含中文乱码解决：Lib\site-packages\django\conf\global_settings.py下的default_charset
	#和file_charset都由utf-8改为gbk

def templateContest(request):
	return render_to_response('kktContest.html', locals())

def templatePresentation(request):
	return render_to_response('kktPresentation.html', locals())	

def templateHabit(request):
	return render_to_response('kktHabit.html', locals())
	
def templateWeather(request):
	return render_to_response('kktWeather.html', locals())
	
def homePage(request):
	f = open(r'I:\2012BS\Website\index\subpage\arvindemo\arvindemo\access_ip_log.txt', 'a')
	ip = "NULL"
	ua = "NULL"
	host = 'NULL'
	try:
		if request.META.has_key('HTTP_X_FORWARDED_FOR'):
			ip =  request.META['HTTP_X_FORWARDED_FOR']
		else:
			ip = request.META['REMOTE_ADDR']
		if request.META.has_key('HTTP_USER_AGENT'):
			ua = request.META['HTTP_USER_AGENT']
		else:
			ua = "NULL"
		if request.META.has_key('HTTP_HOST'):
			host = request.META['HTTP_HOST']
		else:
			host = 'NULL'
		f.write(ip + '--' + host + '--' + ua + '\n')
	except Exception, e:
		f.write(str(e) + '\n')
	f.close()
	return render_to_response('kkt_index.html')
	
def helpPage(request):
	return render_to_response('kktHelp.html')

def server_error(request, template_name='500.html'):
	return render_to_response(template_name,
		context_instance = RequestContext(request)
	)
	
def page404(request):
	return render_to_response('404.html')
	
def submitPage(request):
	post = request.POST
	Mall = 'goodsName'
	Contest = 'ojs'
	Presentation = 'addr'
	WeatherReport = 'city'
	Habit = 'task'
	if Mall in post:
		return submitMall(request)
	elif Contest in post:
		return submitContest(request)
	elif Presentation in post:
		return submitPresentation(request)
	elif Habit in post:
		return submitHabit(request)
	elif WeatherReport in post:
		return submitWeather(request)
	else:
		return HttpResponse(request.POST)
		return HttpResponseRedirect('404')

def submitWeather(request):
	submitInfo = "天气预报信息"
	if 'province' in request.POST:
		pro = request.POST['province'].strip()
		if len(pro) != 0:
			if 'city' in request.POST:
				city = request.POST['city'].strip()
				if len(city) != 0:
					if 'nick' in request.POST:
						nick = request.POST['nick'].strip()
						if len(nick) != 0:
							if 'phone' in request.POST:
									phone = request.POST['phone'].strip()
									if len(phone) == 11 and phone.isdigit():
										weather = weatherReportInfo(province = pro, city = city, phone = phone, name = nick)
										weather.save()
										return render_to_response('cong.html', locals())
	return render_to_response('kktError.html')
	
def submitHabit(request):
	submitInfo = "习惯养成信息"
	if 'motto' in request.POST:
		motto = request.POST['motto'].strip()
		if len(motto) != 0:
			if 'task' in request.POST:
				task = request.POST['task'].strip()
				if len(task) != 0:
					if 'nick' in request.POST:
						nick = request.POST['nick'].strip()
						if len(nick) != 0:
							if 'phone' in request.POST:
								phone = request.POST['phone'].strip()
								if len(phone) == 11 and phone.isdigit():
									if 'hour' in request.POST:
										hour = request.POST['hour'].strip()
										if len(hour) != 0 and hour.isdigit():
											if string.atoi(hour) <= 24 and string.atoi(hour) >= 0:
												habit = habitInfo(motto = motto, task = task, nick = nick, phone = phone, day = 0, hour = hour)
												habit.save()
												return render_to_response('cong.html', locals())
	return render_to_response('kktError.html')
	
def submitPresentation(request):
	submitInfo = "宣讲会信息"
	if 'addr' in request.POST:
		city = request.POST['addr'].strip()
		if len(city) != 0:
			if 'phone' in request.POST:
				phoneNum = request.POST['phone'].strip()
				if len(phoneNum) == 11 and phoneNum.isdigit():
					pret = presentationerInfo(phone = phoneNum, addr = city)
					pret.save()
					return render_to_response('cong.html', locals())
			
	return render_to_response('kktError.html')

def submitMall(request):
	submitInfo = "商品信息"
	name="NULL"
	book=False
	price="-1"
	phoneNum="NULL"
	if 'goodsName' in request.POST:
		name = request.POST['goodsName'].strip()
		if len(name) != 0:
			if 'property' in request.POST:
				book = request.POST['property'].strip()
				if 'price' in request.POST:
					price = request.POST['price'].strip()
					if len(price) != 0 and price.isdigit():
						if 'phone' in request.POST:
							phoneNum = request.POST['phone'].strip()
							if len(phoneNum) == 11 and phoneNum.isdigit():
								customer = customerInfo(goods_name = name, goods_book = (book == '1'), min_price = price, phone = phoneNum)
								customer.save()
								return render_to_response('cong.html', locals())
	return render_to_response('kktError.html')
	
def submitContest(request):
	submitInfo = "比赛信息"
	name="NULL"
	nick="NULL"
	phone="NULL"
	ojs="NULL"
	if 'name' in request.POST:
		name = request.POST['name'].strip()
		if len(name) != 0:
			if 'nick' in request.POST:
				nick = request.POST['nick'].strip()
				if len(nick) != 0:
					if 'phone' in request.POST:
						phone = request.POST['phone'].strip()
						if len(phone) == 11 and phone.isdigit():
							if 'ojs' in request.POST:
								ojs = request.POST['ojs'].strip()
								if len(ojs) != 0:
									participanter = participanterInfo(name=name, nick=nick, phone=phone, ojs=ojs)
									participanter.save()
									return render_to_response('cong.html', locals())
	return render_to_response('kktError.html')
	
def terms(request):
	return render_to_response('kktTerms.html')

def privacy(request):
	return render_to_response('kktPrivacy.html')
	
def about(request):
	return render_to_response('kktAbout.html')

def thanks(request):
	return render_to_response('kktThanks.html')
	
def qa(request):
	return render_to_response('kktQA.html')