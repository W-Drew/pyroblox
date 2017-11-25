'''
Created on Nov 21, 2017

@author: Drew
'''

import queue

from bs4 import BeautifulSoup
import dateutil

from pyroblox.users.user import User

class AuditLog():
	def __init__(self, group, robloxClient):
		self.group = group
		self.robloxClient = robloxClient
		
	def getAuditLogs(self, user=None, action=None):
		logQueue = queue.Queue()
		finished = False
		page = 1
		
		while not finished:
			if logQueue.empty():
				nextPage = self.__getAuditPage(page, user=user, action=action)
				page += 1
				for log in nextPage:
					logQueue.put(log)
		
			if logQueue.empty():
				finished = True
			else:
				yield logQueue.get()
				
	def __getAuditPage(self, page, user=None, action=None):
		url = f"https://www.roblox.com/Groups/Audit.aspx?groupid={self.groupId}"
		params = {
			"pageNum":page, 
			"actionTypeId":(action and action.value or None), 
			"username":(user and user.username or None)
		}
		
		result = self.robloxClient.makeRequestREST("GET", url, params=params)
		htmlPage = BeautifulSoup(result.text, "html.parser")
		logs = htmlPage.findAll("tr", {"class":"datarow"})
		
		for i,log in enumerate(logs):
			timetext = log.find("td", {"class":"Date"}).text
			timestamp = dateutil.parser.parse(timetext)
			rank = log.find("td", {"class":"Rank"}).text.strip()
			username = log.find("td", {"class":"User"}).find("span", {"class":"username"}).text
			userId = int(log.find("td", {"class":"User"}).find("div")["data-user-id"])
			user = User(username=username, userId=userId)
			descriptionElement = log.find("td", {"class":"Description"})
			description = descriptionElement.text
			
			logs[i] = {"user":user, "timestamp":timestamp, "desc":descriptionElement}
		
		return logs
	