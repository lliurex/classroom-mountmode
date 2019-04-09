#!/usr/bin/env python
# -*- coding: utf-8 -*
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GObject,GLib,Gdk,Gio
import os
import signal
import gettext
import sys
import re
import ssl
import xmlrpc.client


signal.signal(signal.SIGINT, signal.SIG_DFL)
_ = gettext.gettext
gettext.textdomain('classroom-mountmode-override')
OVERRIDES_FILE="/etc/classroom-servermode-override"



class OverridesModeManager:
	
	def __init__(self,server=None):
		
		self.debug=False
		
		self.validate_user()
		
	#def init
	
	
	def dprint(self,msg):
		
		if self.debug:
			print(str(msg))
			
	#def dprint
		
	
	def validate_user(self):

		try:
			print("  [Classroom Mount Mode Override]: Checking root")
			f=open("/var/run/ClassMountOverride.token","w")
			f.close()
			os.remove("/var/run/ClassMountOverride.token")
			self.get_overrides_info()


		except Exception as e:
			print(str(e))
			print("  [Classroom Mount Mode Override]: No administration privileges")
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL), "Overrides Classroom Mount Mode")
			dialog.format_secondary_text(_("You need administration privileges to run this application."))
			dialog.run()
			sys.exit(1)
				
	#def validate_user
	
	
	def read_n4dkey(self):

		f=open("/etc/n4d/key")
		key=f.readline().strip("\n")
		f.close()
		return key

	#def read_n4dkey


	def get_overrides_info(self):
		
		server_config=self.get_server_config()
		if server_config["SRV_LITE_MODE"]=="True":
			self.server_mount_mode="Lite"
		else:
			self.server_mount_mode="Full"

		self.server_moving_profiles_enabled=server_config["SRV_MOVING_MODE"]
		self.overrides_server_config=False
		self.overrides_mount_mode=str(server_config["SRV_LITE_MODE"])
		overrides_mount_mode=self.server_mount_mode
		self.overrides_movingprofiles_enabled=self.server_moving_profiles_enabled

		self.dprint("Overrides load info:")
		self.dprint("-Server mount mode: "+self.server_mount_mode)
		self.dprint("-Server moving profiles enabled: "+ str(self.server_moving_profiles_enabled))

		if os.path.exists(OVERRIDES_FILE):
			self.overrides_server_config=True
			overrides_config=self.read_overrides_file()
			self.overrides_mount_mode=overrides_config["SRV_LITE_MODE"]
			if self.overrides_mount_mode=="True":
				overrides_mount_mode="Lite"
			else:
				overrides_mount_mode="Full"	

			self.overrides_movingprofiles_enabled=overrides_config["SRV_MOVING_MODE"]
				
		self.dprint("-Overrides server config: "+str(self.overrides_server_config))
		self.dprint("-Overrides mount mode: "+overrides_mount_mode)
		self.dprint("-Overrides moving profiles enabled: "+str(self.overrides_movingprofiles_enabled))			
		
	#def get_overrides_info
	
	def get_server_config(self):

		server_config={}
		context=ssl._create_unverified_context()	
		client=xmlrpc.client.ServerProxy("https://localhost:9779",allow_none=True,context=context)
		u=self.read_n4dkey()
		server_config["SRV_LITE_MODE"]=str(client.get_variable(u,"VariablesManager","SRV_LITE_MODE"))
		server_config["SRV_MOVING_MODE"]=str(client.get_variable(u,"VariablesManager","SRV_MOVING_MODE"))

		return server_config

	#def get_server_config	

	def read_overrides_file(self):
		
		overrides_config={}
		f=open(OVERRIDES_FILE,'r')
		for line in f.readlines():
			key,tmp=line.split("=")
			value=tmp.split(";")[0].split('"')[1]
			overrides_config[key]=value
		f.close()

		return overrides_config

	#def read_overrides_file	

	def save_overrides_mountmode(self,info):

		self.dprint("Overrides save info: ")
		self.dprint("-Overrides server config: "+str(info[0]))
		if info[1]=="True":
			overrides_mount_mode="Lite"
		else:
			overrides_mount_mode="Full"	
		self.dprint("-Overrides mount mode: "+overrides_mount_mode)
		self.dprint("-Overrides moving profiles enabled: "+str(info[2]))

		if not info[0]:
			self.dprint("Removing overrides_file")
			if os.path.exists(OVERRIDES_FILE):
				os.remove(OVERRIDES_FILE)
		else:
			self.dprint("Saved changes in overrides file")
			self.write_overrides_file(info[1],info[2])

	#def save_overrides_mountmode
		
	def write_overrides_file(self,mount_mode,moving_profiles_enabled):

		lines=['SRV_LITE_MODE="'+str(mount_mode)+'"','SRV_MOVING_MODE="'+str(moving_profiles_enabled)+'"']
		f=open(OVERRIDES_FILE,'w')
		for item in lines:
			f.write(item+'\n')
		f.close()
			
		
	#def write_overrides_file
	
	
#class OverridesModeManager
