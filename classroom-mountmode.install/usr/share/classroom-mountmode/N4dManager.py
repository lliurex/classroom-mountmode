import threading
import time
import n4d.client


class N4dManager:
	
	def __init__(self,server=None):
		
		self.debug=False
		
		self.client=None
		self.user_validated=False
		self.user_groups=[]
		self.validation=None
		self.litemode_status=False
		self.movingprofiles_status=True
		
		'''
		if server!=None:
			self.set_server(server)
		'''
	#def init
	
	
	def dprint(self,msg):
		
		if self.debug:
			print(str(msg))
			
	#def dprint
		
	'''
	def set_server(self,server):
		
		context=ssl._create_unverified_context()	
		self.client=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
	'''	
	#def set_server
	
	
	def validate_user(self,server,user,password):
		
		try:
			self.client=n4d.client.Client("https://%s:9779"%server,user,password)
			
			ret=self.client.validate_user()
			self.user_validated=ret[0]
			self.user_groups=ret[1]
				
			
			if self.user_validated:
				t=self.client.get_ticket()
				if t.valid():
					self.client=n4d.client.Client(ticket=t)
					self.get_server_info()
				else:
					self.user_validated=False
		
		except Exception as e:
			self.dprint("Classroom mount mode info. Validation Error: %s"%str(e))
			self.user_validated=False
					
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
			#Old n4d:ret=self.client.is_lite_enabled(self.validation,"ClassroomMountModeManager")
			return self.client.ClassroomMountModeManager.is_lite_enabled()

		except Exception as e:
			print(str(e))
			
		return False
		
	#def is_litemode_enabled
	
	def is_movingprofiles_enabled(self):
		
		try:
			#Old n4d: ret=self.client.is_moving_profiles_enabled(self.validation,"ClassroomMountModeManager")
			return self.client.ClassroomMountModeManager.is_moving_profiles_enabled()

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
		#Old n4d:ret=self.client.set_lite_mode(self.validation,"ClassroomMountModeManager",status)
		ret=self.client.ClassroomMountModeManager.set_lite_mode(status)
		self.dprint("-N4d response lite mode saved: " +str(ret))
		
	#def set_litemode_status


	def set_movingprofiles_status(self,status):
		
		self.dprint("-Moving profiles enabled: "+str(status))
		#Old n4d: ret=self.client.set_moving_mode(self.validation,"ClassroomMountModeManager",status)
		ret=self.client.ClassroomMountModeManager.set_moving_mode(status)
		self.dprint("-N4d response moving profiles saved: " +str(ret))
	
	#def set_movingprofile_status
	
	
	
#class N4dManager
