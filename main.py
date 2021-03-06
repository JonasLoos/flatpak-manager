#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import subprocess
import sys

# global vars
VERSION = "0.3.2"
run_app_btn_current_handler = 0
flatpak_list_apps = []
flatpak_list_runtimes = []
flatpak_list_remotes = []


# ----- functions -----

def flatpak_run(command):
	try:
		return subprocess.run(['flatpak', *command.split(" ")], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
	except Exception as e:
		print("an error occured while running a flatpak command: ", e.args, file=sys.stderr)

def flatpak_list_run(command):
	return subprocess.run(['flatpak', "list"], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

def show_installed_info(app_name):
	global run_app_btn_current_handler
	print("show " + app_name)
	gtk_installed_stack_main.set_visible_child(gtk_installed_info)
	if run_app_btn_current_handler > 0:
		gtk_installed_info_run_btn.disconnect(run_app_btn_current_handler)
	run_app_btn_current_handler = gtk_installed_info_run_btn.connect("clicked", lambda x: run_app(app_name))
	# set details
	gtk_installed_info_name.set_text(app_name)
	gtk_installed_info_text.set_text(flatpak_run("info " + app_name))


def run_app(app_name):
	print("run " + app_name)
	subprocess.Popen(["flatpak", "run", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def install_app_from_file(filename):
	# input validation
	if len(filename.split()) != 1 or filename.split(".")[-1] != "flatpakref":
		print("try to install illegal file: " + filename)
		return
	print("installing " + filename)
	subprocess.Popen(["x-terminal-emulator", "-e", "bash -c 'flatpak install "+filename+"; read -n 1 -s -p \"done, press any key to exit\"'"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def go_back():
	site = gtk_stack.get_visible_child_name()
	print("go back: " + site)
	if site == "Installed":
		gtk_installed_stack_main.set_visible_child(gtk_installed_list)

def init_installed_list(selected_list, items):
	for line in selected_list.get_children():
		selected_list.remove(line)
	for x in items:
		if len(x) > 0:
			app_name = x.split()[0]
			item = Gtk.Label()
			item.set_text(app_name)
			item.set_xalign(0)
			selected_list.add(item)
	selected_list.show_all()

def load_flatpak_stuff():
	global flatpak_list_apps
	global flatpak_list_runtimes
	global flatpak_list_remotes

	# check if flatpak is installed
	if (flatpak_run("--version") is None):
		print("flatpak doesn't seem to be installed", file=sys.stderr)
		exit()

	# installed
	flatpak_list_apps = flatpak_run("list --app").split("\n")
	init_installed_list(gtk_installed_list_apps, flatpak_list_apps)
	flatpak_list_runtimes = flatpak_run("list --runtime").split("\n")
	init_installed_list(gtk_installed_list_runtimes, flatpak_list_runtimes)


	# remotes
	flatpak_list_remotes = flatpak_run("remotes").split("\n")
	for line in gtk_remotes_list.get_children():
		gtk_remotes_list.remove(line)
	for x in flatpak_list_remotes:
		if len(x) > 0:
			item = Gtk.Label()
			item.set_text(x.split()[0] + " ("+x.split()[1]+")")
			item.set_xalign(0)
			gtk_remotes_list.add(item)
	gtk_remotes_list.show_all()


	# info
	gtk_info_version.set_text(VERSION)
	gtk_about_window.set_version(VERSION)
	# set flatpak version & arch stuff 
	gtk_info_flatpak_version.set_text(flatpak_run("--version"))
	gtk_info_flatpak_supported_arches.set_text(flatpak_run("--supported-arches").replace("\n", ", "))
	gtk_info_flatpak_default_arch.set_text(flatpak_run("--default-arch"))
	gtk_info_flatpak_installed_apps_count.set_text(str(len(flatpak_list_apps)))
	gtk_info_flatpak_installed_runtimes_count.set_text(str(len(flatpak_list_runtimes)))


def init():

	# main 
	# disable file install button
	gtk_home_install_file_button.set_sensitive(False)

	load_flatpak_stuff()

	# about
	gtk_about_window.set_version(VERSION)


	# command line args / file given
	if(len(sys.argv) > 1):
		print(str(len(sys.argv)) + " args given")

		if(sys.argv[1].split(".")[-1] == "flatpakref"):
			print("flatpakref as arg given")
			gtk_home_install_file_chooser.set_filename(sys.argv[1])
			Handler.install_from_file_selected(None)



# ----- gtk handler -----

class Handler:
	def on_destroy(self, *args):
		Gtk.main_quit()
		exit()

	def on_key_pressed(self, widget, event):
		print("Handler: on_key_pressed: " + str(event.keyval))
		# str+f

		# back
		if event.keyval == 65288:
			go_back()

	def on_search_requested(self, *args):
		gtk_stack.set_visible_child(gtk_search)
		search_input_clear()
	
	def search_input_focus():
		gtk_search_input.grab_focus()
		# TODO select all

	def show_about_window(self, *args):
		gtk_about_window.show_all()
		gtk_popover1.hide()
		return True

	def hide_about_window(self, *args):
		gtk_about_window.hide()
		return True

	def show_installed_info_app(self, *args):
		index = args[1].get_index()
		print("show app info: " + str(index) + " - " + flatpak_list_apps[index].split()[0])
		show_installed_info(flatpak_list_apps[index].split()[0])
	def show_installed_info_runtime(self, *args):
		index = args[1].get_index()
		print("show runtime info: " + str(index) + " - " + flatpak_list_runtimes[index].split()[0])
		show_installed_info(flatpak_list_runtimes[index].split()[0])

	def on_go_back_btn_clicked(self, *args):
		go_back()


	def on_reload_pressed(self, *args):
		load_flatpak_stuff()


	def install_from_file_selected(self, *args):
		print("install from file selected called")
		filename = gtk_home_install_file_chooser.get_filename()
		if filename.split(".")[-1] != "flatpakref":
			gtk_home_install_file_button.set_label("(file not supported)")
			gtk_home_install_file_button.set_sensitive(False)
			return
		file = open(filename, "r")
		text = file.read().split("\n")
		file.close()
		infos = {}
		for line in text:
			tmp = line.split("=")
			if len(tmp) == 2:
				infos[tmp[0]] = tmp[1]
		gtk_home_install_file_button.set_label("install " + infos["Name"] + " (" + infos["Branch"] + ") ?")
		gtk_home_install_file_button.set_sensitive(True)

	def install_from_file_button_pressed(self, *args):
		print("install from file button pressed")
		install_app_from_file(gtk_home_install_file_chooser.get_filename())



# ----- bla bla bla -----

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
builder.connect_signals(Handler())


# ----- get stuff -----

gtk_window = builder.get_object("window1")

gtk_go_back_btn = builder.get_object("go_back_btn")

gtk_stack = builder.get_object("stack1")

gtk_home = builder.get_object("home")
gtk_home_install_file_chooser = builder.get_object("install_file_chooser")
gtk_home_install_file_button = builder.get_object("install_file_button")

gtk_updates = builder.get_object("updates")

gtk_installed_stack_main = builder.get_object("installed_stack_main")
gtk_installed_stack_list = builder.get_object("installed_stack_list")
gtk_installed_list = builder.get_object("installed_list")
gtk_installed_list_apps = builder.get_object("installed_list_apps")
gtk_installed_list_runtimes = builder.get_object("installed_list_runtimes")
gtk_installed_info = builder.get_object("installed_info")
gtk_installed_info_name = builder.get_object("installed_info_name")
gtk_installed_info_run_btn = builder.get_object("installed_info_run_btn")
gtk_installed_info_text = builder.get_object("installed_info_text")

gtk_search = builder.get_object("search")
gtk_search_input = builder.get_object("search_input")

gtk_remotes = builder.get_object("remotes")
gtk_remotes_list = builder.get_object("remotes_list")

gtk_info = builder.get_object("info")
gtk_info_version = builder.get_object("info_version")
gtk_info_flatpak_version = builder.get_object("info_flatpak_version")
gtk_info_flatpak_supported_arches = builder.get_object("info_flatpak_supported_arches")
gtk_info_flatpak_default_arch = builder.get_object("info_flatpak_default_arch")
gtk_info_flatpak_installed_apps_count = builder.get_object("info_flatpak_installed_apps_count")
gtk_info_flatpak_installed_runtimes_count = builder.get_object("info_flatpak_installed_runtimes_count")

gtk_popover1 = builder.get_object("popover1")
gtk_about_window = builder.get_object("about_window")

# ----- init -----
init()
gtk_window.show_all()

# ----- whatever -----

Gtk.main()
exit()
