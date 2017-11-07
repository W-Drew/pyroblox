'''
Created on Oct 3, 2017

@author: Drew
'''

def getUsernameFromId(robloxClient, userId):
	url = "https://api.roblox.com/users/"+str(userId)
	return robloxClient.makeRequestREST("GET", url).json()["Username"]
	
def getUserIdFromName(robloxClient, username):
	url = "https://api.roblox.com/users/get-by-username"
	params = [("username", username)]
	return robloxClient.makeRequestREST("GET", url, params=params).json()["Id"]

class User(object):

	def __init__(self, robloxClient, username=None, userId=None):
		if not (username or userId):
			raise ValueError("Attempted to create user with neither username nor userId")
		
		self.robloxClient = robloxClient
		self.username = username or getUsernameFromId(robloxClient, userId)
		self.userId = userId or getUserIdFromName(robloxClient, username)
		
	def isInGroup(self, groupId):
		baseUrl = "https://assetgame.roblox.com/Game/LuaWebService/HandleSocialRequest.ashx"
		params = [("method", "IsInGroup"), ("playerid", self.userId), ("groupid", groupId)]
		
		return "true" in self.robloxClient.makeRequestREST("GET", baseUrl, params=params).text