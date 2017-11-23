'''
Created on Oct 2, 2017

@author: Drew
'''

import requests
from bs4 import BeautifulSoup

fiddlerEnabled = False #Toggle SSL verification since Fiddler breaks it

class RobloxClient(object):

	def __init__(self, username, password):
		self.session = requests.Session()
		self.username = username
		self.xsrfToken = None
		
		self.authenticateRoblox(username, password)
	
	#returns userId, else errors if unsuccessful login
	def authenticateRoblox(self, username, password):
		data = {"username":username, "password":password}
		
		#With 2-Step disabled
		#status_code = 200, data = JSON:{"userId":34534506}
		#With 2-Step enabled
		#status_code = 200, data= JSON:{"tl":"f191ad51-8579-4936-b0b9-4c8f32560330","mediaType":"Email","message":"TwoStepverificationRequired"}
		result = self.session.post("https://api.roblox.com/v2/login", data=data, verify=not fiddlerEnabled)
		jsonResult = result.json()
	
		if jsonResult.get("tl"):
			twoStepUrl = "https://api.roblox.com/v2/twostepverification/login/verify"
			twoStepData = {"IdentificationCode":None, "RememberDevice":False, "tl":jsonResult["tl"], "UserName":username}
			
			while True:
				userInput = input("Enter Verification Code: ").strip()
				twoStepData["IdentificationCode"] = userInput
	
				#status_code = 200, data= JSON:{"isValid":true,"userId":1273918}
				result = self.session.post(twoStepUrl, data=twoStepData)
				jsonResult = result.json()
			
				if result.status_code == 403:
					print("'"+twoStepData["IdentificationCode"]+"'", "was not the correct auth code")
					continue
				
				break
			
		assert result.status_code == 200, "Error ("+str(result.status_code)+") : "+jsonResult["errors"][0]["message"]
		return jsonResult["userId"]
	
	def makeRequestREST(self, method, url, **args):
		if not "headers" in args:
			args["headers"] = {}

		args["headers"]["X-CSRF-TOKEN"] = self.xsrfToken
		
		result = self.session.request(method, url, verify=not fiddlerEnabled, **args)
		if result.status_code == 403 and "X-CSRF-TOKEN" in result.headers: #403 XSRF Token Validation Failed
			self.xsrfToken = result.headers["X-CSRF-TOKEN"]

			return self.makeRequestREST(method, url, **args)
		
		return result
	
	def makeRequestASP(self, url, events, isMultipart=False):
		result = self.makeRequestREST("GET", url)
		htmlPage = BeautifulSoup(result.text, "html.parser")
		inputs = ["__VIEWSTATE","__VIEWSTATEGENERATOR","__EVENTVALIDATION","__RequestVerificationToken"]
		data = {}
		
		for input in inputs:
			data[input] = htmlPage.find("input", {"name":input})["value"]
			
		for event,value in events.items():
			data[event] = value
			
		result = None
		if isMultipart:
			for key,value in data.items():
				if not isinstance(value, tuple):
					data[key] = (None, value)
				
			result = self.makeRequestREST("POST", url, files=data)
		else:
			result = self.makeRequestREST("POST", url, data=data)
		
		return result