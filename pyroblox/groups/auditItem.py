import re as regex
from enum import Enum

import bs4

class AuditAction(Enum):
	DeletePost = 1
	RemoveMember = 2
	AcceptJoinRequest = 3
	DeclineJoinRequest = 4
	PostStatus = 5
	ChangeRank = 6
	BuyAd = 7
	SendAllyRequest = 8
	CreateEnemy = 9
	AcceptAllyRequest = 10
	DeclineAllyRequest = 11
	DeleteAlly = 12
	DeleteEnemy = 13
	AddGroupPlace = 14
	RemoveGroupPlace = 15
	CreateItems = 32
	ConfigureItems = 33
	SpendGroupFunds = 34
	ChangeOwner = 35
	Delete = 36
	Rename = 37
	AdjustCurrencyAmounts = 38
	Abandon = 39
	Claim = 40
	InviteToClan = 41
	KickFromClan = 42
	CanceClanInvite = 43
	BuyClan = 44
	ChangeDescription = 45
	CreateGroupAsset = 47
	UpdateGroupAsset = 48
	ConfigureGroupAsset = 49
	RevertGroupAsset = 50
	CreateGroupDeveloperProduct = 51
	ConfigureGroupGame = 53
	Lock = 90
	Unlock = 91
	CreateGamePass = 92

def getMap():
	return {
		AuditAction.DeletePost: DeletePostItem
	}
actionMap = None

def generateAuditItem(user, timestamp, descriptionElement, actionType=None):
	log = None
	
	if actionType is not None:
		cls = actionMap[actionType]
		log = cls.tryCreate(user, timestamp, descriptionElement)
	else:
		for actionType,cls in actionMap.items():
			log = cls.tryCreate(user, timestamp, descriptionElement)
			if log:
				break
			
	return log	

def matchFields(description, *args):
	args = iter(args)
	objects = []
	text = ""

	for element in description.contents:
		type = next(args)
		
		value = None
		if type == User:
			value = getUserFromElement(element)
		elif type == Group:
			value = getGroupFromElement(element)
		elif type == str:
			value = getTextFromElement(element)
		else:
			raise TypeError("Unsupported field type: "+str(type))
		
		if value is None:
			return None
		elif type == str:
			text += value
		else:
			objects.append(value)
	
	return (text,)+tuple(objects)

def getTextFromElement(element):
	if not isinstance(element, bs4.element.NavigableString):
		return None
	
	return element

def getUserFromElement(element):
	if element.name != "a":
		return None
	
	href = regex.search("/User\.aspx\?ID=(\d+)", element["href"])
	if href is None:
		return None
	
	name = element.text
	id = int(href.group(1))
	return User(username=name, userId=id)

def getGroupFromElement(element):
	if element.name != "a":
		return None
	
	href = regex.search("/Groups/group\.aspx\?gid=(\d+)", element["href"])
	if href is None:
		return None
	
	id = int(href.group(1))
	return Group(id)

def getGameFromElement(element):
	if element.name != "a":
		return None
	
	href = regex.search("/games/(\d+)/.+", element["href"])
	if href is None:
		return None
	
	id = int(href.group(1))
	#return Game(id)

class AuditItem:
	def __init__(self, user, timestamp):
		self.user = user
		self.timestamp = timestamp
		
class PurchaseItem():
	def __init__(self, amount):
		self.amount = amount
		
class TargetedItem():
	def __init__(self, target):
		self.target = target
		
class DeletePostItem(AuditItem, TargetedItem):
	@staticmethod
	def tryCreate(user, timestamp, description):
		result = matchFields(description, User, str, User, str)
		if result is None:
			return None
		
		text,_,target = result
		match = regex.search(" deleted post \"(.+)\" by user \.", text)
		if match is None:
			return None
		
		return DeletePostItem(user, timestamp, target, match.group(1))

	def __init__(self, user, timestamp, target, postText):
		AuditItem.__init__(self, user, timestamp)
		TargetedItem.__init__(self, target)
		self.postText = postText
		
	def __str__(self):
		return f"({self.__class__.__name__}) From {self.user} On {self.target} Message: \"{self.postText}\""
		
actionMap = getMap()