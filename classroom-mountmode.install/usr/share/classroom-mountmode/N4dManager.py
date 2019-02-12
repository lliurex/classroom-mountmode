import xmlrpc.client
import ssl
import threading
import time


class N4dManager:
	
	def __init__(self,server=None):
		
		self.debug=False
		
		self.client=None
		self.user_validated=False
		self.user_groups=[]
		self.validation=None
		self.litemode_status=False
		self.movingprofiles_status=True
		
		if server!=None:
			self.set_server(server)
		
	#def init
	
	
	def dprint(self,msg):
		
		if self.debug:
			print(str(msg))
			
	#def dprint
		
	
	def set_server(self,server):
		
		context=ssl._create_unverified_context()	
		self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
		
	#def set_server
	
	
	def validate_user(self,user,password):
		
		ret=self.client.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.validation=(user,password)
			self.get_server_info()
					
		return self.user_validated
		
	#def validate_user

	def get_server_info(self):

		self.litemode_status=self.is_litemode_enabled()
		self.dprint("Classroom mount mode info: ")
		self.dprint("-Lite mode enabled: "+str(self.litemode_status))
		self.movingprofiles_status=self.is_movingprofiles_enabled()
		self.dprint("-Moving profiles enabled: "+str(self.movingprofiles_status))

	#def get_server_info
	
	def is_litemode_enabled(self):
		
		try:
			ret=self.client.is_lite_enabled(self.validation,"ClassroomMountModeManager")
			if ret["status"]:
				return ret["msg"]
				
		except Exception as e:
			print(str(e))
			
		return False
		
	#def is_litemode_enabled
	
	def is_movingprofiles_enabled(self):
		
		try:
			ret=self.client.is_moving_profiles_enabled(self.validation,"ClassroomMountModeManager")
			if ret["status"]:
				return ret["msg"]
				
		except Exception as e:
			print(str(e))
			
		return False
	
	#def is_movingprofile_enabled
		
	def save_mountmode_config(self,litemode_status,movingprofiles_status):

		self.set_litemode_status(litemode_status)
		self.set_movingprofiles_status(movingprofiles_status)

	#def save_mountmode_config
	
	def set_litemode_status(self,status):
		
		self.dprint("Classroom mount mode save changes")
		self.dprint("-Lite mode enabled: "+str(status))
		ret=self.client.set_lite_mode(self.validation,"ClassroomMountModeManager",status)
		self.dprint("-N4d response lite mode saved: " +str(ret))
		
	#def set_litemode_status


	def set_movingprofiles_status(self,status):
		
		self.dprint("-Moving profiles enabled: "+str(status))
		ret=self.client.set_moving_mode(self.validation,"ClassroomMountModeManager",status)
		self.dprint("-N4d response moving profiles saved: " +str(ret))
	
	#def set_movingprofile_status
	
	
	
#class N4dManager
