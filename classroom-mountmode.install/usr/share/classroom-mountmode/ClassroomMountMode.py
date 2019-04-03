#!/usr/bin/env python
# -*- coding: utf-8 -*

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,GObject,GLib,Gdk,Gio

import signal
import gettext
import sys
import threading
import copy
import os

import N4dManager

signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.textdomain('classroom-mountmode')
_ = gettext.gettext

RSRC_PATH="/usr/share/classroom-mountmode/rsrc/"
CSS_FILE=RSRC_PATH+"style.css"
UI_FILE=RSRC_PATH+"classroom-mountmode.ui"
ENABLED_IMG=RSRC_PATH+"enabled.svg"
DISABLED_IMG=RSRC_PATH+"disabled.svg"
MANAGE_IMG=RSRC_PATH+"manage.svg"

class ClassroomMountMode:
	
	def __init__(self,args_dic):
		
		self.n4d_man=N4dManager.N4dManager()
		self.n4d_man.set_server(args_dic["server"])

		#self.n4d_man.set_server(args_dic["172.20.9.246"])
		
		if args_dic["gui"]:
			
			self.start_gui()
			GObject.threads_init()
			Gtk.main()
		
	#def __init__(self):
	
	
	def start_gui(self):

		builder=Gtk.Builder()
		builder.set_translation_domain('classroom-mountmode')
		builder.add_from_file(UI_FILE)
			
		self.main_window=builder.get_object("main_window")
		
		self.main_box=builder.get_object("main_box")
		self.login_box=builder.get_object("login_box")
		self.servermode_box=builder.get_object("servermode_box")

		self.stack=Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack.set_transition_duration(200)
		self.stack.add_titled(self.login_box,"login","Login")
		self.stack.add_titled(self.servermode_box,"servermode","Server Mode")
		self.stack.show_all()
		
		self.main_box.pack_start(self.stack,True,True,0)
		
		self.login_button=builder.get_object("login_button")
		self.user_entry=builder.get_object("user_entry")
		self.password_entry=builder.get_object("password_entry")
		self.server_ip_entry=builder.get_object("server_ip_entry")
		self.login_msg_label=builder.get_object("login_msg_label")
		
		self.servermode_label=builder.get_object("servermode_label")
		self.servermode_separator=builder.get_object("servermode_separator")
		self.mode_label=builder.get_object("mode_label")
		self.mode_entry_label=builder.get_object("mode_entry_label")
		self.mode_btn=builder.get_object("mode_btn")
		self.modes_popover=builder.get_object("modes_popover")
		self.fullmode_btn=builder.get_object("fullmode_btn")
		self.litemode_btn=builder.get_object("litemode_btn")
		self.movingprofiles_status_box=builder.get_object("movingprofiles_status_box")
		self.movingprofiles_label=builder.get_object("movingprofiles_label")
		self.movingprofiles_status_label=builder.get_object("movingprofiles_status_label")
		self.movingprofiles_btn=builder.get_object("movingprofiles_btn")

		self.label_list=[self.mode_label,self.mode_entry_label,self.movingprofiles_label,self.movingprofiles_status_label]
		
		self.lite_separator=builder.get_object("lite_separator")
		self.info_label=builder.get_object("info_label")

		self.msg_label=builder.get_object("msg_label")

		self.help_btn=builder.get_object("help_btn")
		self.apply_btn=builder.get_object("apply_btn")
				
		self.login_button.grab_focus()
		
		self.init_threads()
		self.connect_signals()
		self.set_css_info()
		self.main_window.show()
		self.help_btn.hide()
		self.orig_values=[]
		
	#def start_gui
	
	


	def init_threads(self):

		self.open_help_t=threading.Thread(target=self.open_help)
		self.open_help_t.daemon=True

		GObject.threads_init()
	
	#def init_threads

	def connect_signals(self):
		
		self.main_window.connect("destroy",Gtk.main_quit)
		self.main_window.connect("delete_event",self.check_changes)
		self.login_button.connect("clicked",self.login_clicked)
		self.user_entry.connect("activate",self.entries_press_event)
		self.password_entry.connect("activate",self.entries_press_event)
		self.server_ip_entry.connect("activate",self.entries_press_event)
		self.mode_btn.connect("clicked",self.mode_btn_clicked)
		self.fullmode_btn.connect("clicked",self.set_fullmode)
		self.litemode_btn.connect("clicked",self.set_litemode)
		self.movingprofiles_btn.connect("clicked",self.movingprofiles_status_changed)
		self.help_btn.connect("clicked",self.show_help)
		self.apply_btn.connect("clicked",self.apply_changes)

		
	#def connect_signals
	
	# CSS ###########################################################

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(CSS_FILE)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WHITE-BACKGROUND")
		self.user_entry.set_name("CUSTOM-ENTRY")
		self.password_entry.set_name("CUSTOM-ENTRY")
		self.server_ip_entry.set_name("CUSTOM-ENTRY")

		self.servermode_label.set_name("HEADER-LABEL")
		self.servermode_separator.set_name("HEADER-SEPARATOR")

		for item in self.label_list:
			item.set_name("INFO-LABEL")

		self.mode_btn.set_name("MANAGE_BUTTON")	
		self.fullmode_btn.set_name("POPOVER_BUTTON")
		self.litemode_btn.set_name("POPOVER_BUTTON")

		self.lite_separator.set_name("HEADER-SEPARATOR")
		self.info_label.set_name("DEFAULT-LABEL-HELP")
		self.msg_label.set_name("MSG-LABEL")

	#def set_css_info		
	
	# SIGNALS ########################################################
	
	def entries_press_event(self,widget):
		
		self.login_clicked(None)
		
	#def entries_press_event
	
	
	def login_clicked(self,widget):
		
		user=self.user_entry.get_text()
		password=self.password_entry.get_text()
		server=self.server_ip_entry.get_text()
	
		'''	
		# HACK
		
		user="lliurex"
		password="lliurex"
		server="172.20.9.246"
		'''

		if server!="":
			self.n4d_man.set_server(server)
		else:
			self.n4d_man.set_server('server')
		
		self.login_msg_label.set_text(_("Validating user..."))
		
		self.login_button.set_sensitive(False)
		self.validate_user(user,password)
		
		
	#def login_clicked

	def mode_btn_clicked(self,widget):

		self.msg_label.set_text("")
		self.modes_popover.show()
		
	#def mode_btn_clicked	

	def set_litemode(self,widget):

		self.modes_popover.hide()
		self.msg_label.set_text("")
		self.mode_entry_label.set_text(_("Lite"))
		self.litemode_state=True
		self.movingprofiles_btn.set_sensitive(True)
		self.movingprofiles_manage_state(self.movingprofiles_status_orig)

	#def set_litemode

	def set_fullmode(self,widget):

		self.modes_popover.hide()
		self.msg_label.set_text("")
		self.mode_entry_label.set_text(_("Full"))
		self.litemode_state=False
		self.movingprofiles_btn.set_sensitive(False)
		self.movingprofiles_manage_state(True)

	#def set_fullmode


	def movingprofiles_status_changed(self,widget):

		self.msg_label.set_text("")
		if self.movingprofiles_state:
			self.movingprofiles_status_orig=False
			self.movingprofiles_manage_state(False)
		else:
			self.movingprofiles_status_orig=True
			self.movingprofiles_manage_state(True)	

	#def movingprofiles_status_changed
	
	def apply_changes(self,widget):
		
		self.orig_values=[copy.deepcopy(self.litemode_state),copy.deepcopy(self.movingprofiles_state)]
		self.msg_label.set_text("")
		self.n4d_man.save_mountmode_config(self.litemode_state,self.movingprofiles_state)
		self.msg_label.set_markup("<b>"+_("Changes applied successful")+"</b>")
		
	#def apply_changes

	def show_help(self,widget):

		lang=os.environ["LANG"]

		if 'ca_ES' in lang:
			self.help_cmd='xdg-open http://wiki.lliurex.net/tiki-index.php?page='
		else:
			self.help_cmd='xdg-open http://wiki.lliurex.net/tiki-index.php?page='

		self.init_threads()
		self.open_help_t.start()

	#def show_help	

	def open_help(self):

		os.system(self.help_cmd)

	#def open_help	

	
	def litemode_manage_state(self,litemode_status,movingprofiles_status):

		self.litemode_state=litemode_status

		if self.litemode_state:
			self.mode_entry_label.set_text(_("Lite"))
			self.movingprofiles_btn.set_sensitive(True)

		else:
			self.mode_entry_label.set_text(_("Full"))
			self.movingprofiles_btn.set_sensitive(False)
	

		self.movingprofiles_manage_state(movingprofiles_status)	

	#def litemode_manage_state		


	def movingprofiles_manage_state(self,movingprofiles_status):

		self.movingprofiles_state=movingprofiles_status

		if self.movingprofiles_state:
			self.movingprofiles_status_label.set_text(_("Enabled"))
			img=Gtk.Image.new_from_file(ENABLED_IMG)
			self.movingprofiles_btn.set_image(img)
			if self.litemode_state:
				self.movingprofiles_btn.set_name("ENABLED_BUTTON")
				self.movingprofiles_btn.set_tooltip_text(_("Press to disable moving profiles"))

		else:
			self.movingprofiles_status_label.set_text(_("Disabled"))
			img=Gtk.Image.new_from_file(DISABLED_IMG)
			self.movingprofiles_btn.set_image(img)
			if self.litemode_state:
				self.movingprofiles_btn.set_name("DISABLED_BUTTON")
				self.movingprofiles_btn.set_tooltip_text(_("Press to enable moving profiles"))

		if not self.litemode_state:
			self.movingprofiles_btn.set_name("BUTTON_LOCK")
			self.movingprofiles_btn.set_tooltip_text(_("To change the status of moving profiles it is \n necessary that the established mode be Lite"))			

	#def movingprofiles_manage_state		

	# ##################### ##########################################
	
	def validate_user(self,user,password):
		
		
		t=threading.Thread(target=self.n4d_man.validate_user,args=(user,password,))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.validate_user_listener,t)
		
	#def validate_user
	
	
	def validate_user_listener(self,thread):
			
		if thread.is_alive():
			return True
				
		self.login_button.set_sensitive(True)
		if not self.n4d_man.user_validated:
			self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user")+"</span>")
		else:
			group_found=False
			for g in ["adm","admins","teachers"]:
				if g in self.n4d_man.user_groups:
					group_found=True
					break
					
			if group_found:
				self.login_msg_label.set_text("")
				self.movingprofiles_status_orig=self.n4d_man.movingprofiles_status
				self.orig_values=[copy.deepcopy(self.n4d_man.litemode_status),copy.deepcopy(self.n4d_man.movingprofiles_status)]
				self.litemode_manage_state(self.n4d_man.litemode_status,self.movingprofiles_status_orig)
				self.stack.set_visible_child_name("servermode")
				
			else:
				self.login_msg_label.set_markup("<span foreground='red'>"+_("Invalid user")+"</span>")
				
		return False
			
	#def validate_user_listener
	
	def check_changes(self,widget,event=None):

		pending_changes=0

		if len(self.orig_values)>0:
		
			if self.orig_values[0]!=self.litemode_state:
				pending_changes+=1

			if self.orig_values[1]!=self.movingprofiles_state:
				pending_changes+=1

			if pending_changes>0:
				dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,
	             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),"Classroom Mount Mode")
				dialog.format_secondary_text(_("There are pending changes to apply. Do you want to exit or cancel?"))
				response=dialog.run()
				dialog.destroy()
				if response==Gtk.ResponseType.CLOSE:
					return False
				else:
					return True

		sys.exit(0)

	#def check_changes
		
#class LliurexShutdowner


if __name__=="__main__":
	
	pass
	
