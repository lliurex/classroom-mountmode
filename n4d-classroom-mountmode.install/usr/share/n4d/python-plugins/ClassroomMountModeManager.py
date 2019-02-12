

class ClassroomMountModeManager:
	
	def __init__(self):
		
		self.lite_status=False
		self.moving_status=False

	#def init
	
	
	def startup(self,options):
		
		self.init_variable()
		
	#def startup
	
	
	def init_variable(self):
		
		self.n4d_vars=objects["VariablesManager"]
		
		self.lite_status=objects["VariablesManager"].get_variable("SRV_LITE_MODE")
		self.moving_status=objects["VariablesManager"].get_variable("SRV_MOVING_MODE")
		
		
		if self.lite_status==None:
			try:
				self.n4d_vars.add_variable("SRV_LITE_MODE",False,"","Classroom Mount mode configuration","classroom-mount-mode")
			except Exception as e:
				pass
			self.lite_status=False

		if self.moving_status==None:
			try:
				self.n4d_vars.add_variable("SRV_MOVING_MODE",False,"","Classroom Moving configuration for lite mode","classroom-mount-mode")
			except Exception as e:
				pass
			self.moving_status=False
		
	#def init_variable
	
	
	
	def is_lite_enabled(self):
		
		return {"status":True, "msg":self.lite_status}
		
	#def is_lite_enabled
	
	
	def is_moving_profiles_enabled(self):
		
		return {"status":True, "msg":self.moving_status}
		
	#def is_lite_enabled
	
	
	def set_lite_mode(self,value):
	
		if type(value)==bool:
			try:
				self.n4d_vars.set_variable("SRV_LITE_MODE",value)
				self.lite_status=value
				return {"status":True, "msg":""}
			except Exception as e:
				return {"status":False, "msg":str(e)}
				
		else:
			return {"status":False, "msg":"Value is not boolean"}
	
	#def set_lite_mode
	
	
	def set_moving_mode(self,value):
	
		if type(value)==bool:
			try:
				self.n4d_vars.set_variable("SRV_MOVING_MODE",value)
				self.moving_status=value
				return {"status":True, "msg":""}
			except Exception as e:
				return {"status":False, "msg":str(e)}
				
		else:
			return {"status":False, "msg":"Value is not boolean"}
	
	#def set_lite_mode
	
	
#class ClassroomMountManager
