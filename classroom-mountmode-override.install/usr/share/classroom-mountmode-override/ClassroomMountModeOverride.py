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
import pwd

import OverridesModeManager

signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.textdomain('classroom-mountmode-override')
_ = gettext.gettext

RSRC_PATH="/usr/share/classroom-mountmode-override/rsrc/"
CSS_FILE=RSRC_PATH+"style.css"
UI_FILE=RSRC_PATH+"classroom-mountmode-override.ui"
ENABLED_IMG=RSRC_PATH+"enabled.svg"
DISABLED_IMG=RSRC_PATH+"disabled.svg"
MANAGE_IMG=RSRC_PATH+"manage.svg"

class ClassroomMountModeOverride:
	
	def __init__(self,args_dic):
		
		self.overrides_man=OverridesModeManager.OverridesModeManager()
		if args_dic["gui"]:
			try:
				user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
				home_path="/home/"+user+"/.config"
				os.environ["XDG_CONFIG_DIRS"]="/etc/xdg/xdg-/usr/share/xsessions/plasma:/etc/xdg:"+home_path
			except:
				pass
			self.start_gui()
			Gtk.main()
		
	#def __init__(self):
	
	
	def start_gui(self):

		builder=Gtk.Builder()
		builder.set_translation_domain('classroom-mountmode-override')
		builder.add_from_file(UI_FILE)
			
		self.main_window=builder.get_object("main_window")
		self.main_window.resize(705,654)
		self.main_box=builder.get_object("main_box")
		self.info_box=builder.get_object("info_box")

		self.stack=Gtk.Stack()
		self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack.set_transition_duration(200)
		self.stack.add_titled(self.info_box,"overridesmode","Overrides Mode")
		self.stack.show_all()
		
		self.main_box.pack_start(self.stack,True,True,0)
		
		
		serverinfo_label=builder.get_object("serverinfo_label")
		servermode_separator=builder.get_object("servermode_separator")
		server_mode_label=builder.get_object("server_mode_label")
		self.server_mode_entry_label=builder.get_object("server_mode_entry_label")
		self.server_movingprofiles_label=builder.get_object("server_movingprofiles_label")
		self.server_movingprofiles_entry_label=builder.get_object("server_movingprofiles_entry_label")
		overrides_option_label=builder.get_object("overrides_option_label")
		self.overrides_option_switch=builder.get_object("overrides_option_switch")
		overrides_mode_label=builder.get_object("overrides_mode_label")
		self.overrides_mode_entry_label=builder.get_object("overrides_mode_entry_label")
		self.overrides_mode_btn=builder.get_object("overrides_mode_btn")
		self.overrides_modes_popover=builder.get_object("overrides_modes_popover")
		self.fullmode_btn=builder.get_object("fullmode_btn")
		self.litemode_btn=builder.get_object("litemode_btn")
		overrides_movingprofiles_label=builder.get_object("overrides_movingprofiles_label")
		self.overrides_movingprofiles_entry_status=builder.get_object("overrides_movingprofiles_entry_status")
		self.overrides_movingprofiles_btn=builder.get_object("overrides_movingprofiles_btn")

		config_separator=builder.get_object("config_separator")
		
		self.info_label=builder.get_object("info_label")

		self.msg_label=builder.get_object("msg_label")

		self.help_btn=builder.get_object("help_btn")
		self.apply_btn=builder.get_object("apply_btn")

		self.header_list=[serverinfo_label]
		self.label_list=[server_mode_label,self.server_mode_entry_label,self.server_movingprofiles_label,self.server_movingprofiles_entry_label,overrides_option_label,overrides_mode_label,self.overrides_mode_entry_label,overrides_movingprofiles_label,self.overrides_movingprofiles_entry_status]
		self.separator_list=[servermode_separator,config_separator]
				
		
		self.set_css_info()
		self.init_threads()
		self.orig_values=[]
		self.load_mount_mode()
		self.apply=False
		self.connect_signals()
		self.main_window.show()
		
				
	#def start_gui


	def init_threads(self):

		self.open_help_t=threading.Thread(target=self.open_help)
		self.open_help_t.daemon=True

		GObject.threads_init()
	
	#def init_threads

	
	def connect_signals(self):
		
		self.main_window.connect("destroy",Gtk.main_quit)
		self.main_window.connect("delete_event",self.check_changes)
		self.overrides_option_switch.connect("notify::active",self.overrides_option_switch_changed)
		self.overrides_mode_btn.connect("clicked",self.overrides_mode_btn_clicked)
		self.fullmode_btn.connect("clicked",self.set_fullmode)
		self.litemode_btn.connect("clicked",self.set_litemode)
		self.overrides_movingprofiles_btn.connect("clicked",self.overrides_movingprofiles_btn_clicked)
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

		for item in self.header_list:
			item.set_name("HEADER-LABEL")

		for item in self.separator_list:
			item.set_name("HEADER-SEPARATOR")

		for item in self.label_list:
			item.set_name("INFO-LABEL")

		self.overrides_mode_btn.set_name("MANAGE_BUTTON")	
		self.fullmode_btn.set_name("POPOVER_BUTTON")
		self.litemode_btn.set_name("POPOVER_BUTTON")
		self.info_label.set_name("DEFAULT-LABEL-HELP")
		self.msg_label.set_name("MSG-LABEL")

	#def set_css_info		
	
	# SIGNALS ########################################################
	
	def overrides_mode_btn_clicked(self,widget):

		self.msg_label.set_text("")
		self.overrides_modes_popover.show()

	#def overrides_mode_btn_clicked	

	def set_litemode(self,widget):

		self.overrides_modes_popover.hide()
		self.msg_label.set_text("")
		self.overrides_mode_entry_label.set_text(_("Lite"))
		self.overrides_movingprofiles_btn.set_sensitive(True)
		self.overrides_mode_set="True"
		self.movingprofiles_manage_state(self.movingprofiles_enabled_orig)

	#def set_litemode

	def set_fullmode(self,widget):

		self.overrides_modes_popover.hide()
		self.msg_label.set_text("")
		self.overrides_mode_entry_label.set_text(_("Full"))
		self.overrides_mode_set="False"
		self.overrides_movingprofiles_btn.set_sensitive(False)
		self.movingprofiles_manage_state("True")

	#def set_fullmode


	def overrides_movingprofiles_btn_clicked(self,widget):

		self.msg_label.set_text("")
		if self.overrides_movingprofiles_set=="True":
			self.movingprofiles_enabled_orig="False"
			self.movingprofiles_manage_state("False")
		else:
			self.movingprofiles_enabled_orig="True"
			self.movingprofiles_manage_state("True")	

	#def movingprofiles_enabled_changed
	
	def load_mount_mode(self):

		self.server_mode_entry_label.set_text(_(self.overrides_man.server_mount_mode))
		if self.overrides_man.server_moving_profiles_enabled=="True":
			self.server_movingprofiles_entry_label.set_text(_("Enabled"))
		else:
			self.server_movingprofiles_entry_label.set_text(_("Disabled"))

		self.overrides_server_config=self.overrides_man.overrides_server_config
		self.overrides_mode_set=self.overrides_man.overrides_mount_mode
		self.movingprofiles_enabled_orig=self.overrides_man.overrides_movingprofiles_enabled
		self.overrides_option_switch.set_active(self.overrides_server_config)

		self.orig_values=[copy.deepcopy(self.overrides_server_config),copy.deepcopy(self.overrides_mode_set),copy.deepcopy(self.movingprofiles_enabled_orig)]
	
		if not self.overrides_server_config:
			self.overrides_mode_btn.set_name("BUTTON_DISABLE")
		else:
			self.overrides_mode_btn.set_name("MANAGE_BUTTON")	
		
		if self.overrides_mode_set=="False":
			self.overrides_mode_entry_label.set_text(_("Full"))
			self.overrides_movingprofiles_btn.set_sensitive(False)

		else:
			self.overrides_mode_entry_label.set_text(_("Lite"))
			if self.overrides_server_config:
				self.overrides_movingprofiles_btn.set_sensitive(True)	
			else:
				self.overrides_movingprofiles_btn.set_sensitive(False)	
		
		
		self.overrides_option_switch_managed()
		self.movingprofiles_manage_state(self.movingprofiles_enabled_orig)	

	#def load_mount_mode		


	def movingprofiles_manage_state(self,movingprofiles_enabled):

		self.overrides_movingprofiles_set=movingprofiles_enabled

		if self.overrides_movingprofiles_set=="True":
			self.overrides_movingprofiles_entry_status.set_text(_("Enabled"))
			img=Gtk.Image.new_from_file(ENABLED_IMG)
			self.overrides_movingprofiles_btn.set_image(img)
		
		else:
			self.overrides_movingprofiles_entry_status.set_text(_("Disabled"))
			#self.server_movingprofiles_entry_label.set_text(_("Disabled"))
			img=Gtk.Image.new_from_file(DISABLED_IMG)
			self.overrides_movingprofiles_btn.set_image(img)
		
		if self.overrides_server_config:
			
			if self.overrides_mode_set=="True":
				if self.overrides_movingprofiles_set=="True":
					self.overrides_movingprofiles_btn.set_tooltip_text(_("Press to disable moving profiles"))
					self.overrides_movingprofiles_btn.set_name("MOVING_ENABLED_BUTTON")
				else:
					self.overrides_movingprofiles_btn.set_tooltip_text(_("Press to enable moving profiles"))
					self.overrides_movingprofiles_btn.set_name("MOVING_DISABLED_BUTTON")	

			else:
				self.overrides_movingprofiles_btn.set_name("BUTTON_LOCK")
				self.overrides_movingprofiles_btn.set_tooltip_text(_("To change the status of moving profiles it is \n necessary that the established mode be Lite"))			
		else:
			self.overrides_movingprofiles_btn.set_name("BUTTON_DISABLE")		

	#def movingprofiles_manage_state	

	def apply_changes(self,widget):
		

		self.msg_label.set_text("")
		info=[self.overrides_server_config,self.overrides_mode_set,self.overrides_movingprofiles_set]
		self.orig_values=copy.deepcopy(info)
		self.overrides_man.save_overrides_mountmode(info)
		self.msg_label.set_markup("<b>"+_("Changes applied successful")+"</b>")
		
	#def apply_changes

	def overrides_option_switch_managed(self):

		if self.overrides_server_config:
			self.overrides_option_switch.set_tooltip_text(_("Deactivate to apply server configuration"))
		else:
			self.overrides_option_switch.set_tooltip_text(_("Activate to override server configuration"))

	#def overrides_option_switch_managed
	
	def overrides_option_switch_changed(self,widget,data):
		
		self.overrides_server_config=widget.get_active()

		if widget.get_active():
			self.overrides_mode_btn.set_name("MANAGE_BUTTON")
			self.overrides_mode_btn.set_sensitive(True)

			if self.overrides_mode_set =="True":
				self.overrides_movingprofiles_btn.set_sensitive(True)
			else:
				self.overrides_movingprofiles_btn.set_sensitive(False)
		else:
			self.overrides_mode_btn.set_name("BUTTON_DISABLE")
			self.overrides_mode_btn.set_sensitive(False)
			self.overrides_movingprofiles_btn.set_sensitive(False)

		self.overrides_option_switch_managed()	
		self.movingprofiles_manage_state(self.overrides_movingprofiles_set)

						
	#def overrides_option_switch_changed

	def show_help(self,widget):

		lang=os.environ["LANG"]
		language=os.environ["LANGUAGE"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True

		exec_lang=""
		app_lang=""

		if language=="":
			app_lang=lang
		else:
			language=language.split(":")[0]
			app_lang=language
	
		
		if 'valencia' in app_lang:
			exec_lang="LANG=ca_ES.UTF-8@valencia"
			cmd=exec_lang+' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Classroom-Mount-Mode-Override.'
		else:
			exec_lang="LANG=es_ES.UTF-8"
			cmd=exec_lang+' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Classroom-Mount-Mode-Override'

		if not run_pkexec:
			self.fcmd="su -c '%s' $USER "%cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ "' "+ user
		
		self.init_threads()
		self.open_help_t.start()

	#def show_help	

	def open_help(self):

		os.system(self.fcmd)

	#def open_help	

	def check_changes(self,widget,event=None):

		pending_changes=0
		if len(self.orig_values)>0:
			if self.orig_values[0]!=self.overrides_server_config:
				pending_changes+=1

			if self.overrides_server_config:
				if self.orig_values[1]!=self.overrides_mode_set:
					pending_changes+=1

				if self.orig_values[2]!=self.overrides_movingprofiles_set:
					pending_changes+=1

			if pending_changes>0:
				dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),"Classroom Mount Mode Override")
				dialog.format_secondary_text(_("There are pending changes to apply. Do you want to exit or cancel?"))
				response=dialog.run()
				dialog.destroy()
				if response==Gtk.ResponseType.CLOSE:
					return False
				else:
					return True

		sys.exit(0)

	#def check_changes	
		
#class OverridesClassroomMountMode


if __name__=="__main__":
	
	pass
	
