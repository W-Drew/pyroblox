'''
Created on Nov 23, 2017

@author: Drew
'''
import re as regex
import requests

from bs4 import BeautifulSoup

def userIdFromText(text):
	return int(regex.search("\d+", text).group(0))

def getUsernameFromId(userId):
	url = "https://api.roblox.com/users/"+str(userId)
	result = requests.get(url)
	
	return result.json()["Username"]
	
def getUserIdFromName(username):
	url = "https://api.roblox.com/users/get-by-username"
	params = {"username": username}
	result = requests.get(url, params=params)
	
	return result.json()["Id"]

def getUsernameHistory(user):
	url = f"https://www.roblox.com/users/{user.userId}/profile"
	result = requests.get(url)
	htmlPage = BeautifulSoup(result.text, "html.parser")
	
	pastNamesElement = htmlPage.find("span", {"class":"tooltip-pastnames"})
	pastNamesListText = pastNamesElement["title"]
	pastNamesList = pastNamesListText.split(", ")
	pastNamesList.insert(0, user.username)
	
	return pastNamesList

class User(object):

	def __init__(self, username=None, userId=None):
		if not (username or userId):
			raise ValueError("Attempted to create user with neither username nor userId")
		
		self.__username = username
		self.__userId = userId
		self.__pastUsernames = None
		
	def __str__(self):
		return "User("+str(self.userId)+":"+self.username+")"
	
	def __repr__(self):
		return self.__str__()
	
	def __eq__(self, other):
		return self.userId == other.userId
	
	@property
	def userId(self):
		if self.__userId is None:
			self.__userId = getUserIdFromName(self.__username)
		
		return self.__userId
	
	@property
	def username(self):
		if self.__username is None:
			self.__username = getUsernameFromId(self.__userId)
			
		return self.__username
	
	@property
	def pastUsernames(self):
		if self.__pastUsernames is None:
			pastNamesListUnique = list(set(getUsernameHistory(self)))
			pastNamesListUnique.remove(self.username)
			self.__pastUsernames = pastNamesListUnique
		
		return self.__pastUsernames