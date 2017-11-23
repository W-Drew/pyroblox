'''
Created on Nov 21, 2017

@author: Drew
'''
import re as regex
import requests

from bs4 import BeautifulSoup

from users.user import User
from groups.role import Role

def getUserGroups(user):
	url = f"https://api.roblox.com/users/{user.userId}/groups"
	result = requests.get(url)
	
	groupDataList = result.json()
	groupList = [Group(entry["Id"]) for entry in groupDataList]
	
	return groupList

def getUserRoleInGroup(user, group):
	url = f"https://assetgame.roblox.com/Game/LuaWebService/HandleSocialRequest.ashx"
	params = {"method":"GetGroupRole", "playerid":user.userId, "groupid":group.groupId}
	result = requests.get(url, params=params)
	
	roleName = result.text
	for role in group.roles:
		if role.name == roleName:
			return role	

class Group():
	def __init__(self, groupId):
		# Attributes
		self.groupId = groupId
		
		# Lazy Properties
		self.__name = None
		self.__owner = None
		self.__emblemUrl = None
		self.__description = None
		self.__roles = None
		self.__allies = None
		self.__enemies = None
		self.__numMembers = None
	
	def __str__(self):
		return "Group("+str(self.groupId)+":"+self.name+")"
	
	def __repr__(self):
		return self.__str__()
	
	def __eq__(self, other):
		return self.groupId == other.groupId
	
	@property
	def name(self):
		if self.__name is None:
			self.__populateGroupProperties()
			
		return self.__name
	
	@property
	def owner(self):
		if self.__owner is None:
			self.__populateGroupProperties()
				
		return self.__owner
	
	@property
	def emblemUrl(self):
		if self.__emblemUrl is None:
			self.__populateGroupProperties()
				
		return self.__emblemUrl
	
	@property
	def description(self):
		if self.__description is None:
			self.__populateGroupProperties()
				
		return self.__description
	
	@property
	def roles(self):
		if self.__roles is None:
			self.__populateGroupRoles()
			
		return self.__roles
	
	@property
	def allies(self):
		if self.__allies is None:
			self.__allies = self.__getGroupRelationsOfType("allies")
		
		return self.__allies
	
	@property
	def enemies(self):
		if self.__enemies is None:
			self.__enemies = self.__getGroupRelationsOfType("enemies")
		
		return self.__enemies
	
	@property
	def numMembers(self):
		if self.__numMembers is None:
			self.__populateMemberMetadata()
		
		return self.__numMembers
	
	def __populateGroupProperties(self):
		url = f"https://api.roblox.com/groups/{self.groupId}"
		result = requests.get(url)
		
		groupData = result.json()
		
		self.__name = groupData["Name"]
		self.__emblemUrl = groupData["EmblemUrl"]
		self.__description = groupData["Description"]
		self.__owner = User(
			userId=groupData["Owner"]["Id"], 
			username=groupData["Owner"]["Name"]
		)
		
	def __populateGroupRoles(self):
		url = f"https://www.roblox.com/api/groups/{self.groupId}/RoleSets"
		result = requests.get(url)
		
		roleData = result.json()
		roles = []
		for entry in roleData:
			role = Role(entry["Name"], entry["Rank"], entry["Id"])
			roles.append(role)
		
		self.__roles = roles
		
	def __populateMemberMetadata(self):
		url = f"https://www.roblox.com/my/groups.aspx?gid={self.groupId}"
		result = requests.get(url)
		htmlPage = BeautifulSoup(result.text, "html.parser")
		
		memberText = htmlPage.find("div", {"id":"MemberCount"}).text
		self.__numMembers = int(regex.search("\d+", memberText).group(0))
		
	def __getGroupRelationsOfType(self, relationType):
		url = f"https://api.roblox.com/groups/{self.groupId}/{relationType}"
		finished = False
		groups = []
		page = 1
				
		while not finished:
			params = {"page":page}
			result = requests.get(url, params=params)
			data = result.json()
			page += 1
			
			finished = data["FinalPage"]
			for groupData in data["Groups"]:
				group = Group(groupData["Id"])
				groups.append(group)
				
		return groups
	
	###      TODO       ###
	'''
		Get group's games
		
		Get group's assets/etc
	
		Reporting
			- Wall post
			- Shout
			- Group
			- Rank name
			
		Audit Log
		
		Publishing Assets
			- Manage games
			- Upload model
			- Upload audio
			- Upload clothing/etc
			
		Advertise Group
			- Upload ad
			- Run ad
		
		Revenue Log
		
		Set group funds publicly visible
		
		Set group games publicly visible
		
		Add/delete role
		
		Change role name/rank/description
		
		Change role permissions		
		
		DANGER ZONE:
			Group Payouts
			
			Change Owner
			
			
	'''