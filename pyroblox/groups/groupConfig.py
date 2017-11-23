'''
Created on Nov 23, 2017

@author: Drew
'''

class GroupConfig():
	def __init__(self, group, robloxClient):
		self.group = group
		self.robloxClient = robloxClient
		
	def setEmblem(self, file):
		url = f"https://www.roblox.com/my/groupadmin.aspx?gid={self.group.groupId}"
		source = file.read()
		
		events = {
			"__EVENTTARGET":"ctl00$ctl00$cphRoblox$cphMyRobloxContent$UploadNewEmblemButton",
			"__EVENTARGUMENT":"",
			"ctl00$ctl00$cphRoblox$cphMyRobloxContent$UpdateEmblemFileUpload": ("emblem.png", source, "image/png")
		}
		
		result = self.robloxClient.makeRequestASP(url, events, isMultipart=True)
	
	def setDescription(self, text):
		url = f"https://www.roblox.com/my/groupadmin.aspx?gid={self.group.groupId}"
		events = {
			"__EVENTTARGET":"ctl00$ctl00$cphRoblox$cphMyRobloxContent$UploadNewEmblemButton",
			"__EVENTARGUMENT":"",
			"ctl00$ctl00$cphRoblox$cphMyRobloxContent$GroupDescription": text
		}
		
		result = self.robloxClient.makeRequestASP(url, events, isMultipart=True)