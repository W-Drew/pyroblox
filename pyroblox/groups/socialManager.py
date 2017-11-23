'''
Created on Nov 23, 2017

@author: Drew
'''
import queue

from bs4 import BeautifulSoup

class SocialManager():
	def __init__(self, group, robloxClient):
		self.group = group
		self.robloxClient = robloxClient
		
	def getWallPosts(self, sortOrder="Desc"):
		postQueue = queue.Queue()
		pageSize = 10
		finished = False
		cursor = None
		
		while not finished:
			if postQueue.empty():
				nextPage = self.__getWallPage(sortOrder, pageSize, cursor)
				
				cursor = nextPage["nextPageCursor"]
				for postData in nextPage["data"]:
					post = postData #WallPost(postData)
					postQueue.put(post)
		
			if postQueue.empty():
				finished = True
			else:
				yield postQueue.get()
	
	def makeWallPost(self, text):
		url = f"https://www.roblox.com/my/groups.aspx?gid={self.group.groupId}"
		events = {
			"ctl00$cphRoblox$GroupWallPane$NewPost": text,
			"ctl00$cphRoblox$GroupWallPane$NewPostButton":"Post",
		}
		
		result = self.robloxClient.makeRequestASP(url, events)
	
	def deleteWallPost(self, post):
		url = f"https://groups.roblox.com/v1/groups/{self.group.groupId}/wall/posts/{post.id}"

		result = self.robloxClient.makeRequestREST("DELETE", url)
	
	def getShout(self):
		url = f"https://m.roblox.com/groups/{self.group.groupId}"
		
		headers = {"User-Agent":"Android Mobile"}#Requires specific keywords from normal User-Agent to prevent redirects 
		result = self.robloxClient.makeRequestREST("GET", url, headers=headers)
			
		htmlPage = BeautifulSoup(result.text, "html.parser")
		if not htmlPage.find("div", {"class":"group-shout"}):
			raise PermissionError("Insufficient permissions to view group shout")
		
		if htmlPage.find("div", {"class":"group-shout-body"}).text == "":
			return None
		
		#shout = Shout(htmlPage)
		
		#return shout
	
	def makeShout(self, text):
		url = f"https://www.roblox.com/my/groups.aspx?gid={self.group.groupId}"
		events = {
			"ctl00$cphRoblox$GroupStatusPane$StatusTextBox": text,
			"ctl00$cphRoblox$GroupStatusPane$StatusSubmitButton":"Group Shout",
		}
		
		result = self.robloxClient.makeRequestASP(url, events)	
		
	def __getWallPage(self, sortOrder, pageSize, cursor):
		url = f"https://groups.roblox.com/v1/groups/{self.group.groupId}/wall/posts"
		params = {"sortOrder":sortOrder, "limit":pageSize, "cursor":cursor}
		
		result = self.robloxClient.makeRequestREST("GET", url, params=params)
		return result.json()