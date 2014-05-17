#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright (C) 2014 KodeKarnage
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#


import xbmcgui
import xbmc
import xbmcaddon
import sys
import os
import shutil
import re


__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__setting__      = __addon__.getSetting
lang             = __addon__.getLocalizedString
dialog           = xbmcgui.Dialog()

scriptPath       = __addon__.getAddonInfo('path')
user_data = xbmc.translatePath( "special://userdata")



def log(message, label = ''):
	logmsg       = '%s : %s - %s ' % (__addonid__, label, message)
	xbmc.log(msg = logmsg)





		



class main:

	def __init__(self):
		self.data_file = os.path.join(user_data,'addon_data',__addonid__,'settings.xml')
		self.as_file = os.path.join(user_data,'advancedsettings.xml')
		self.settings_file= os.path.join(scriptPath,'resources','settings.xml')

		self.data_file_pattern_id = ' id=[\'"](.*?)[\'"]'
		self.data_file_pattern_value = ' value=[\'"](.*?)[\'"]'
		self.as_file_pattern_id = '<!--(.*?)>'
		self.as_file_pattern_sub = '>.*<'

		self.check_files()

		__addon__.openSettings()

		self.read_settings()
		self.create_new_as()


	def check_files(self):
		log(self.data_file, 'data_file location')
		log(os.path.isfile(self.data_file), 'file exists?')
		log(self.as_file, 'advanced settings file location')
		log(os.path.isfile(self.as_file), 'file exists?')
		log(self.settings_file, 'addon settings file location')
		log(os.path.isfile(self.settings_file), 'file exists?')

		if not os.path.isfile(self.as_file):
			try:
				with open(self.as_file, 'w+') as f:
					pass
			except IOError:
				log('cannot create advanced settings file')
				sys.exit()
			except:
				log(sys.exc_info()[0], 'Unexpected error, advanced settings file check')


	def create_new_as(self):

		new_lines = []

		# open data_file, load lines into memory

		with open(self.settings_file, 'r') as f:
			lines = f.readlines()
			for line in lines:
				if '<!--' in line:
					new_lines.append(line)


		with open(self.as_file, 'w+') as f:
			for line in new_lines:
				if "<!--" in line:
					if "_HEADING" in line:
						f.write(line.replace("_HEADING",'').replace('!--','').replace('-->','>') )
					else:
						findid = re.findall('<!--(.*?)>',line)
						if findid and findid[0] in self.active_settings:
							active_setting_line = re.sub(self.as_file_pattern_sub, '>' + self.settings_dict[findid[0]] + '<', line)
							log(active_setting_line)

							f.write(active_setting_line.replace('!--','').replace('-->','>') )







	def read_settings(self):



		self.settings_dict = {}

		with open(self.data_file,'r') as f:
			lines = f.readlines()
			for line in lines:
				if re.findall(self.data_file_pattern_id, line):
					self.settings_dict[re.findall(self.data_file_pattern_id, line)[0]] = re.findall(self.data_file_pattern_value, line)[0]

		self.active_settings = [x.replace('bool','') for x in self.settings_dict.keys() if x.endswith('bool') and self.settings_dict[x] == 'true']
		log(self.active_settings)



'''


# Opening
	- read as.xml, 
		check if each item is in settings.xml or in the addondata file (<!-- + item), 
		if in settings.xml but not addondata file then alter addondata (via setSettings) to reflect value in as.xml
		there can be no situation where it is in the addondata but not in settings.xml
		if not in either then save to the side for addition to file later
			- need to save parents of these lines, so the reader will need to keep track of items opening and Closing
			- then when it is being saved back, the writer will have to check whether the parent structure is being replicated and bring in those extra lines

	- Open Settings



# Closing
	- create new as.xml
	- bring in lines saved from previous opening



'''
if __name__ == "__main__":
	main()

