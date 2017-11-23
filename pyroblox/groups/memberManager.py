'''
Created on Nov 23, 2017

@author: Drew
'''
from enum import Enum

from bs4 import BeautifulSoup
import dateutil

from users.user import userIdFromText
from users.user import User

class RequestActionType(Enum):
	Pass = 0
	Decline = 1
	Accept = 2
	
class JoinRequest():
	def __init__(self, requestElement):
		username = requestElement.findAll("td")[1].a.string
		userId = userIdFromText(requestElement.findAll("td")[1].a["href"])
		
		self.timestamp = dateutil.parser.parse(requestElement.findAll("td")[2].string)
		self.id =  int(requestElement.findAll("td")[3].span["data-rbx-join-request"])
		self.user = User(username=username,userId=userId)

class MemberManager():
	def __init__(self, group, robloxClient):
		self.robloxClient = robloxClient
		self.group = group
		
		self.__lastIgnoredRequest = None
		
	#AutoApprove or ManualApprove
	def setApprovalType(self, approvalType):
		pass
	
	def processJoinRequests(self, requestActionCallback, defaultRankCallback=None):
		joinRequests = self.__getJoinRequests()		
		if len(joinRequests) == 0:
			return
		
		shouldDeny,shouldAccept = self.__sortJoinRequests(joinRequests, requestActionCallback)
		self.__processJoinRequestsREST(shouldDeny, False)
		self.__processJoinRequestsREST(shouldAccept, True)
		
		if defaultRankCallback:
			for joinRequest in shouldAccept:
				targetRankId = defaultRankCallback(
					joinRequest.user, 
					joinRequest.timestamp
				)
				
				if targetRankId is not None:
					self.setUserRank(joinRequest.user, targetRankId)
				
		self.processJoinRequests(requestActionCallback, defaultRankCallback)#Process next page
	
	#Desc = newest members first
	def getMembersInRank(self, rankId, sortOrder="Desc"):
		#TODO enforce allowed values 10, 25, 50, 100
		url = f"https://groups.roblox.com/v1/groups/{self.group.groupId}/roles/{rankId}/users"
		params = {"sortOrder": sortOrder, "limit": 10, "cursor": None}

		while True:
			resultJson = self.robloxClient.makeRequestREST("GET", url, params=params).json()
			for memberData in resultJson["data"]:
				user = User(
					userId=memberData["userId"], 
					username=memberData["username"]
				)
				yield user
			
			cursor = resultJson["nextPageCursor"]
			if cursor is None:
				break
			else:
				params["cursor"] = cursor
	
	def setUserRank(self, user, rankId):
		url = "https://www.roblox.com/groups/api/change-member-rank"
		data = {"groupId": self.group.groupId, "newRoleSetId": rankId, "targetUserId": user.userId}
		
		result = self.robloxClient.makeRequestREST("POST", url, data=data)
		
		if result.status_code != 200:
			raise RuntimeError("setUserRank on "+str(user)+" to rankId="+str(rankId)+" failed with error: ("+str(result.status_code)+") "+result.reason)
		
		if result.json()["success"] != True:
			raise RuntimeError("Could not set rank of "+str(user)+" to rankId="+str(rankId))
	
	def kickUser(self, user, deletePosts=False):
		url = "https://www.roblox.com/My/Groups.aspx/ExileUserAndDeletePosts"
		data = {
			"userId":user.userId,
			"deleteAllPostsOption":deletePosts,
			"selectedGroupId":self.group.groupId,
			"rolesetId":0 #Required param, but value can be anything
		}
		
		result = self.robloxClient.makeRequestREST("POST", url, json=data)
		
	def __getJoinRequests(self, username=None):
		"""
			#Case 1: No join requests (even without username filter), so list is empty
			#Case 2: Multiple join requests. Search returned all join requests since no filter match
				#NOTE: username filter is exact. It will either return the join request for filter, or all
			#Case 3: Exactly 1 join request, which may/may not match filter
			if len(joinRequestRows) != 1:
				return []
			
			#Case 1: Username matches filter. Search success. This is the join request for provided username
			#Case 2: Username doesn't match filter. Search returned all join requests.
			firstUsername = joinRequestRows[0].findAll("td")[1].a.string
		"""
		url = f"https://www.roblox.com/groups/{self.group.groupId}/joinrequests-html"
		data = [("username", username)]
		
		result = self.robloxClient.makeRequestREST("GET", url, data=data)
		joinRequestRows = BeautifulSoup(result.text, "html.parser")("tr")
		joinRequestRows = joinRequestRows[1:-1] #Trim header/footer rows that aren't join requests
		
		if username is not None:
			# Multiple (filter failed - no join request for username) or no join requests
			if len(joinRequestRows) != 1:
				return []
			
			# Failed filter returns all join requests, but there's only one
			firstUsername = joinRequestRows[0].findAll("td")[1].a.string
			if firstUsername != username:
				return []
		
		joinRequests = [JoinRequest(row) for row in joinRequestRows]
		return joinRequests		
	
	def __sortJoinRequests(self, joinRequests, processTypeCallback):
		shouldDeny,shouldAccept = [],[]
		firstPassed = None
		
		for joinRequest in joinRequests:
			if joinRequest.timestamp <= self.__lastIgnoredRequest:
				break
			
			isUserAllowed = processTypeCallback(joinRequest)
			
			if isUserAllowed == RequestActionType.Pass:
				if firstPassed is None:
					firstPassed = joinRequest.timestamp
			elif isUserAllowed == RequestActionType.Decline:
				shouldDeny.append(joinRequest)
			elif isUserAllowed == RequestActionType.Accept:
				shouldAccept.append(joinRequest)
			
		self.__lastIgnoredRequest = firstPassed or self.__lastIgnoredRequest
		return (shouldDeny,shouldAccept)
	
	def __processJoinRequestsREST(self, joinRequests, shouldAccept):
		if len(joinRequests) == 0:
			return
		
		url = "https://www.roblox.com/group/handle-all-join-requests"
		data = [("groupId", self.group.groupId), ("accept", shouldAccept)]
		for joinRequest in joinRequests:
			data.append(("groupJoinRequestIDs", joinRequest.id))
			
		self.robloxClient.makeRequestREST("POST", url, data=data)