import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
#import os
import subprocess

VERSION = "0.1"



# ----- functions -----

def flatpak_run(command):
	return subprocess.run(['flatpak', *command.split(" ")], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

def flatpak_list_run(command):
	return subprocess.run(['flatpak', "list"], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

# ----- gtk handler -----

class Handler:
	def on_destroy(self, *args):
		Gtk.main_quit()
		#exit()

	def on_key_pressed(self, widget, event):
		pass
		# str+f

	def on_search_requested(self, *args):
		gtk_stack.set_visible_child(gtk_search)
		search_input_clear()
	
	def search_input_focus():
		gtk_search_input.grab_focus()
		# TODO select all


# ----- bla bla bla -----

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
builder.connect_signals(Handler())


# ----- get stuff -----

gtk_window = builder.get_object("window1")
gtk_window.show_all()

gtk_stack = builder.get_object("stack1")

gtk_home = builder.get_object("home")

gtk_updates = builder.get_object("updates")

gtk_installed = builder.get_object("installed")
gtk_installed_stack = builder.get_object("installed_stack")
gtk_installed_list_apps = builder.get_object("installed_list_apps")
gtk_installed_list_runtimes = builder.get_object("installed_list_runtimes")

gtk_search = builder.get_object("search")
gtk_search_input = builder.get_object("search_input")

gtk_settings = builder.get_object("settings")

gtk_info = builder.get_object("info")
gtk_info_version = builder.get_object("info_version")
gtk_info_flatpak_version = builder.get_object("info_flatpak_version")
gtk_info_flatpak_supported_arches = builder.get_object("info_flatpak_supported_arches")
gtk_info_flatpak_default_arch = builder.get_object("info_flatpak_default_arch")
gtk_info_flatpak_installed_apps_count = builder.get_object("info_flatpak_installed_apps_count")
gtk_info_flatpak_installed_runtimes_count = builder.get_object("info_flatpak_installed_runtimes_count")


# ----- init -----

gtk_window.show_all()


# installed

def init_installed_list(selected_list, items):
	for x in items:
		item = Gtk.Label()
		item.set_text(x.split(" ")[0])
		item.set_xalign(0)
		selected_list.add(item)
	selected_list.show_all()

flatpak_list_apps = flatpak_run("list --app").split("\n")
init_installed_list(gtk_installed_list_apps, flatpak_list_apps)

flatpak_list_runtimes = flatpak_run("list --runtime").split("\n")
init_installed_list(gtk_installed_list_runtimes, flatpak_list_runtimes)


# info

gtk_info_version.set_text(VERSION)
# set flatpak version & arch stuff 
gtk_info_flatpak_version.set_text(flatpak_run("--version"))
gtk_info_flatpak_supported_arches.set_text(flatpak_run("--supported-arches").replace("\n", ", "))
gtk_info_flatpak_default_arch.set_text(flatpak_run("--default-arch"))
gtk_info_flatpak_installed_apps_count.set_text(str(len(flatpak_list_apps)))
gtk_info_flatpak_installed_runtimes_count.set_text(str(len(flatpak_list_runtimes)))



Gtk.main()
