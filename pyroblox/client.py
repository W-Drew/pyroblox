'''
Created on Oct 2, 2017

@author: Drew
'''

import requests

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
		result = self.session.post("https://api.roblox.com/v2/login", data=data)
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
	
	def sendPM(self, to, subject, body):
		baseUrl = "https://www.roblox.com/messages/send"
		data = [("recipientId", to), ("subject", subject), ("body", body)]
		
		result = self.makeRequestREST("POST", baseUrl, data=data)
		return result
	
	def makeRequestREST(self, method, url, **args):
		if not "headers" in args:
			args["headers"] = {}

		args["headers"]["X-CSRF-TOKEN"] = self.xsrfToken
		
		result = self.session.request(method, url, **args)
		if result.status_code == 403 and "XSRF" in result.reason: #403 XSRF Token Validation Failed
			self.xsrfToken = result.headers["X-CSRF-TOKEN"]

			return self.makeRequestREST(method, url, **args)
		
		return result
			
	#Ugly hax to get Xsrf token. Thanks Froast.
	def getGeneralXsrfToken(self):
		url = "https://api.roblox.com/sign-out/v1" #Apparently won't sign out since no Xsrf token provided'
		resultHeaders = self.session.post(url).headers
		
		if not "X-CSRF-TOKEN" in resultHeaders:
			raise LookupError("ROBLOX did not provide X-CSRF-TOKEN in response headers")
		
		return resultHeaders["X-CSRF-TOKEN"]