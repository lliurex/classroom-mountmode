#!/usr/bin/python3

import n4d.server.core as n4dcore
import n4d.responses

class ClassroomMountModeManager:
	
	def __init__(self):
		
		self.core=n4dcore.Core.get_core()
		self.lite_status=False
		self.moving_status=False

	#def init
	
	
	def startup(self,options):
		
		self.init_variable()
		
	#def startup
	
	
	def init_variable(self):
		'''
		self.n4d_vars=objects["VariablesManager"]
		
		self.lite_status=objects["VariablesManager"].get_variable("SRV_LITE_MODE")
		self.moving_status=objects["VariablesManager"].get_variable("SRV_MOVING_MODE")
		'''
		self.lite_status=self.core.get_variable("SRV_LITE_MODE").get('return',None)
		self.moving_status=self.core.get_variable("SRV_MOVING_MODE").get('return',None)

		
		if self.lite_status==None:
			try:
				#Old n4d: self.n4d_vars.add_variable("SRV_LITE_MODE",False,"","Classroom Mount mode configuration","classroom-mount-mode")
				self.core.set_variable("SRV_LITE_MODE",False)
			except Exception as e:
				pass
			self.lite_status=False

		if self.moving_status==None:
			try:
				#Old n4d:self.n4d_vars.add_variable("SRV_MOVING_MODE",True,"","Classroom Moving configuration for lite mode","classroom-mount-mode")
				self.core.set_variable("SRV_MOVING_MODE",True)
			except Exception as e:
				pass
			self.moving_status=True
		
	#def init_variable
	
	
	
	def is_lite_enabled(self):
		
		#Old n4d: return {"status":True, "msg":self.lite_status}
		return n4d.responses.build_successful_call_response(self.lite_status)
		
	#def is_lite_enabled
	
	
	def is_moving_profiles_enabled(self):
		
		#Old n4d: return {"status":True, "msg":self.moving_status}
		return n4d.responses.build_successful_call_response(self.moving_status)

		
	#def is_lite_enabled
	
	
	def set_lite_mode(self,value):
	
		if type(value)==bool:
			try:
				#Old n4d: self.n4d_vars.set_variable("SRV_LITE_MODE",value)
				ret=self.core.set_variable("SRV_LITE_MODE",value)
				self.lite_status=value
				#Old n4d: return {"status":True, "msg":""}
				return ret
			except Exception as e:
				#Old n4d: return {"status":False, "msg":str(e)}
				return n4d.responses.build_failed_call_response('',str(e))
				
				
		else:
			#Old n4d: return {"status":False, "msg":"Value is not boolean"}
			return responses.build_failed_call_response('',"Value is not boolean")

	
	#def set_lite_mode
	
	
	def set_moving_mode(self,value):
	
		if type(value)==bool:
			try:
				#Old n4d: self.n4d_vars.set_variable("SRV_MOVING_MODE",value)
				ret=self.core.set_variable("SRV_MOVING_MODE",value)
				self.moving_status=value
				#Old n4d:return {"status":True, "msg":""}
				return ret
			except Exception as e:
				#Old n4d:return {"status":False, "msg":str(e)}
				return responses.build_failed_call_response('',str(e))
				
				
		else:
			#Old n4d: return {"status":False, "msg":"Value is not boolean"}
			return responses.build_failed_call_response('',"Value is not boolean")
			
	#def set_lite_mode
	
	
#class ClassroomMountManager
