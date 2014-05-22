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
import xml.dom.minidom as xdm
import lxml.etree as etree


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




'''
TODO

nested sub menus not in current coverage

whole groups that arent in current coverage

'''

		



class main:

	def __init__(self):
		self.stored_settings_file = os.path.join(user_data,'addon_data',__addonid__,'settings.xml')
		self.as_file = os.path.join(user_data,'advancedsettings.xml')
		self.template_file= os.path.join(scriptPath,'resources','settings.xml')

		self.template_file_pattern_id = ' id=[\'"](.*?)[\'"]'
		self.template_file_pattern_value = ' value=[\'"](.*?)[\'"]'
		self.as_file_pattern_id = '<!--(.*?)>'
		self.as_file_pattern_sub = '>(.*)<'
		self.as_file_pattern_tag = '<(.*?)>'

		self.check_files()

		self.prettify_as_file()

		__addon__.openSettings()
		self.read_files_to_memory()
		self.read_advanced_settings_file()
		self.create_new_as()
		self.prettify_as_file()


	def prettify_as_file(self):
		proc = True

		with open(self.as_file,'r') as f:
			lines = f.readlines()
			if not lines:
				proc = False
				log('ADVANCED SETTINGS FILES IS EMPTY')

		if proc:

			xml = xdm.parse(self.as_file) # or xml.dom.minidom.parseString(xml_string)
			pretty_xml_as_string = [x.strip() for x in xml.toprettyxml().splitlines()]

			with open(self.as_file,'w+') as f:
				log('PRETTIFY WRITING LINES')
				for line in pretty_xml_as_string:
					if line:
						if '<?xml' in line:
							continue
						else:
							f.write(line + '\n')


	def check_files(self):

		log(self.stored_settings_file, 'stored_settings_file location')
		log(os.path.isfile(self.stored_settings_file), 'file exists?')
		log(self.as_file, 'advanced settings file location')
		log(os.path.isfile(self.as_file), 'file exists?')
		log(self.template_file, 'template file location')
		log(os.path.isfile(self.template_file), 'file exists?')

		if not os.path.isfile(self.as_file):
			try:
				with open(self.as_file, 'w+') as f:
					log('ADVANCED SETTINGS FILE CREATED')
					pass
			except IOError:
				log('cannot create advanced settings file')
				sys.exit()
			except:
				log(sys.exc_info()[0], 'Unexpected error, advanced settings file check')


	def create_new_as(self):

		self.reactive_tag = []

		with open(self.as_file, 'w+') as f:
			for line in self.new_lines:
				if "<!--" in line:
					if "_HEADING" in line:
						clean_heading = line.replace("_HEADING",'').replace('!--','').replace('-->','>')
						f.write(clean_heading)
						log(line,'HEADING WRITTEN')
						log(self.reactive_tag,'REACTIVE TAG')

						# get tag in the line

						finds = re.findall(self.as_file_pattern_tag,clean_heading)
						log(finds,'FINDS')
						if finds:
							tag = finds[0]
							log(tag,"TAG")

							if tag[0] == '/':
								tag = tag[1:]

							# update reactive tag list
							if ''.join(['<',tag,'>']) in clean_heading:

								self.reactive_tag.append(tag)

							elif ''.join(['</',tag,'>']) in clean_heading:

								self.reactive_tag.remove(tag)

							# check for items in user dict
							if '|'.join(self.reactive_tag) in self.user_all_settings_dict.keys():
								log('|'.join(self.reactive_tag),'USER SETTING WRITTEN TO')
								for x in self.user_all_settings_dict['|'.join(self.reactive_tag)]:
									f.write(x)
								del self.user_all_settings_dict['|'.join(self.reactive_tag)]

					else:
						findid = re.findall('<!--(.*?)>',line)
						if findid and findid[0] in self.active_settings:
							active_setting_line = re.sub(self.as_file_pattern_sub, '>' + self.all_settings_dict[findid[0]] + '<', line)
							log(active_setting_line, 'SETTING WRITTEN')

							f.write(active_setting_line.replace('!--','').replace('-->','>') )



	def read_advanced_settings_file(self):
		# reads the advanced settings file and extracts any user 

		self.structure_tracker = {}
		self.active_tag = []
		self.user_all_settings_dict = {}

		with open(self.as_file,'r+') as f:
			read_lines = f.readlines()

			for line in read_lines:
				log(self.active_tag,'ACTIVE TAG')
				log(line,"LINE")
				finds = re.findall(self.as_file_pattern_tag,line)
				if finds:
					tag = finds[0]
					log(tag,"TAG")

					if tag[0] == '/':
						tag = tag[1:]

					if '<' + tag + '>' in line and '</' + tag + '>' in line:
						# close tag is present, this is a setting
						log("SETTING")

						if tag not in self.all_settings_dict.keys():
							# if the tag is not one covered by the existing settings
							log('TAG NOT IN ALL_SETTINGS DICT')

							self.user_all_settings_dict['|'.join(self.active_tag)].append(line)

						else:
							# if the tag is one that is covered by the existing settings, use that value
							log('TAG IN ALL_SETTING DICT')

							value = re.findall(self.as_file_pattern_sub, line)
							if value:
								__addon__.setSetting(tag,value[0])


					elif ''.join(['<',tag,'>']) in line:
						log('OPEN')
						# there is an open tag without a close tag, this must be an open tag
						# add to the active tags and create empty list for the key
						self.active_tag.append(tag)
						self.user_all_settings_dict['|'.join(self.active_tag)] = []


					elif ''.join(['</',tag,'>']) in line:
						log('CLOSE TAG')
						# there is a close tag without and open tage, this must be a close tag
						self.active_tag.remove(tag)

					else:
						log(''.join(['</',tag,'>']))


		empty_keys = [k for k,v in self.user_all_settings_dict.iteritems() if not v]
		for k in empty_keys:
			del self.user_all_settings_dict[k]
		log(self.user_all_settings_dict ,'USER SETTINGS')




	def read_files_to_memory(self):

		self.all_settings_dict = {}
		self.new_lines = []
		self.headings = []

		with open(self.template_file,'r') as f:
			lines = f.readlines()

			for line in lines:

				if '<!--' in line:
					self.new_lines.append(line)

				if "_HEADING" in line:
					self.headings.append(line.replace("_HEADING",'').replace('<!--','').replace('-->','').strip())


		with open(self.stored_settings_file,'r') as f:

			lines = f.readlines()

			for line in lines:

				if re.findall(self.template_file_pattern_id, line):
					self.all_settings_dict[re.findall(self.template_file_pattern_id, line)[0]] = re.findall(self.template_file_pattern_value, line)[0]

		
		self.active_settings = [x.replace('bool','') for x in self.all_settings_dict.keys() if x.endswith('bool') and self.all_settings_dict[x] == 'true']
		
		#log(self.all_settings_dict,'SETTINGS DICT')
		
		#log(self.active_settings, 'ACTIVE LIST')

		log(self.headings, 'HEADINGS')

		#log(self.new_lines,'NEW LINES')



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

