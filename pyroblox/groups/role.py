'''
Created on Nov 23, 2017

@author: Drew
'''

class Role():
	def __init__(self, roleName, roleLevel, roleId):
		self.name = roleName
		self.level = roleLevel
		self.id = roleId
		
	def __str__(self):
		return "Role("+self.name+":"+str(self.level)+":"+str(self.id)+")"
	
	def __repr__(self):
		return self.__str__()