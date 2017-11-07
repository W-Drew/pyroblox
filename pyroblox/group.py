'''
Created on Oct 2, 2017

@author: Drew
'''
import re as regex
from enum import Enum

from dateutil import parser
from bs4 import BeautifulSoup

class RequestActionType(Enum):
	Pass = 0
	Decline = 1
	Accept = 2

class GroupClient(object):

	def __init__(self, robloxClient, groupId):
		self.robloxClient = robloxClient
		self.groupId = groupId
		self.lastRequestPassed = None
		
		self.groupApiUrl = "https://groups.roblox.com/v1/groups/"+str(groupId)
		
	def __sortJoinRequests(self, joinRequests, processTypeCallback):
		shouldPass,shouldDeny,shouldAccept = [],[],[]
		
		for joinRequest in joinRequests:
			if joinRequest["UserId"] == self.lastRequestPassed:
				break
			
			isUserAllowed = processTypeCallback(
				joinRequest["Username"], 
				joinRequest["UserId"], 
				joinRequest["Timestamp"]
			)
			
			if isUserAllowed == RequestActionType.Pass:
				shouldPass.append(joinRequest)
			elif isUserAllowed == RequestActionType.Decline:
				shouldDeny.append(joinRequest)
			elif isUserAllowed == RequestActionType.Accept:
				shouldAccept.append(joinRequest)
			
		return (shouldPass,shouldDeny,shouldAccept)	
		
	def processJoinRequests(self, processTypeCallback, defaultRankCallback=None):
		joinRequests = self.__getJoinRequests()		
		if len(joinRequests) == 0:
			return
		
		shouldPass,shouldDeny,shouldAccept = self.__sortJoinRequests(joinRequests, processTypeCallback)
		self.__processJoinRequestsREST(shouldDeny, False)
		self.__processJoinRequestsREST(shouldAccept, True)
		self.lastRequestPassed = shouldPass[0]
		
		if defaultRankCallback is not None:
			for joinRequest in shouldAccept:
				targetRankId = defaultRankCallback(
					joinRequest["Username"], 
					joinRequest["UserId"], 
					joinRequest["Timestamp"]
				)
				
				if targetRankId is not None:
					self.setUserRank(joinRequest["UserId"], targetRankId)
				
		self.processJoinRequests(processTypeCallback, defaultRankCallback)#Process next page
				
	def setUserRank(self, userId, rankId):
		baseUrl = "https://www.roblox.com/groups/api/change-member-rank"
		data = [("groupId", self.groupId), ("newRoleSetId", rankId), ("targetUserId", userId)]
		
		result = self.robloxClient.makeRequestREST("POST", baseUrl, data=data)
		
		if result.status_code != 200:
			raise RuntimeError("setUserRank on userId="+str(userId)+" to rankId="+str(rankId)+" failed with error: ("+str(result.status_code)+") "+result.reason)
		
		if result.json()["success"] != True:
			raise RuntimeError("Could not set rank of userid="+str(userId)+" to rankId="+str(rankId))
	
	def getPagedRankList(self, rankId, startOffset=None, maxUsers=100, sortOrder="Desc"):
		baseUrl = self.groupApiUrl+"/roles/"+str(rankId)+"/users"
		params = [("sortOrder", sortOrder), ("limit", maxUsers),("cursor",startOffset)]

		resultJson = self.robloxClient.makeRequestREST("GET",baseUrl,params=params).json()
		return (resultJson["data"], resultJson["nextPageCursor"])
	
	
	
	
	def __getJoinRequests(self, username=None):
		baseUrl = "https://www.roblox.com/groups/{groupId}/joinrequests-html".format(groupId=self.groupId)
		data = [("username", username)]#Returns 1 if requester with that _exact_ name, else all requests
		result = self.robloxClient.makeRequestREST("GET", baseUrl, data=data)
		
		joinRequestRows = BeautifulSoup(result.content, "html.parser")("tr")
		joinRequestRows = joinRequestRows[1:-1] #Trim header/footer rows that aren't join requests
		
		if username is not None:
			#Case 1: No join requests (even without username filter), so list is empty
			#Case 2: Multiple join requests. Search returned all join requests since no filter match
				#NOTE: username filter is exact. It will either return the join request for filter, or all
			#Case 3: Exactly 1 join request, which may/may not match filter
			if len(joinRequestRows) != 1:
				return []
			
			#Case 1: Username matches filter. Search success. This is the join request for provided username
			#Case 2: Username doesn't match filter. Search returned all join requests.
			firstUsername = joinRequestRows[0].findAll("td")[1].a.string
			if firstUsername != username:
				return []
		
		joinRequests = []
		for joinRequestRow in joinRequestRows:
			joinRequest = {
				"Username": joinRequestRow.findAll("td")[1].a.string,
				"UserId": int(regex.search("\d+", joinRequestRow.findAll("td")[1].a["href"]).group(0)),
				"Timestamp": parser.parse(joinRequestRow.findAll("td")[2].string),
				"RequestId": int(joinRequestRow.findAll("td")[3].span["data-rbx-join-request"])
			}
	
			joinRequests.append(joinRequest)
		
		return joinRequests		
	
	def __processJoinRequestsREST(self, joinRequests, shouldAccept):
		if len(joinRequests) == 0:
			return
		
		url = "https://www.roblox.com/group/handle-all-join-requests"
		data = [("groupId", self.groupId), ("accept", shouldAccept)]
		for joinRequest in joinRequests:
			joinRequestId = joinRequest["RequestId"]
			data.append(("groupJoinRequestIDs", joinRequestId))
			
		self.robloxClient.makeRequestREST("POST", url, data=data)