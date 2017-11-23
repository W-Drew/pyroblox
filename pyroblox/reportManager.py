'''
Created on Nov 23, 2017

@author: Drew
'''

from enum import Enum

class ReportCategory(Enum):
	InappropriateLanguage = 1
	PrivateInformation = 2
	Harassment = 3
	Dating = 4
	Exploiting = 5
	AccountTheft = 6
	InappropriateAsset = 7
	RealLifeThreat = 8
	Other = 9

class ReportManager():
	def __init__(self, robloxClient):
		self.robloxClient = robloxClient
		
	def reportWallPost(self, post, *args):
		url = f"https://www.roblox.com/abusereport/groupwallpost?id={post.id}"
		self.__makeReport(url, *args)
		
	def reportShout(self, group, *args):
		url = f"https://www.roblox.com/abuseReport/groupstatus?id={group.groupId}"
		self.__makeReport(url, *args)
		
	def reportGroup(self, group, *args):
		url = f"https://www.roblox.com/abusereport/group?id={group.groupId}"
		self.__makeReport(url, *args)
		
	def __makeReport(self, url, category, comment):
		events = {
			"ReportCategory":category.value,
			"Comment":comment
		}
		
		self.robloxCLient.makeRequestASP(url, events)