#! /usr/bin/env python

# fbk_sanitize.py -- A python script to sanitize wall posts from a facebook export file based on timestamp 
# 	(through a user-provided newline-separated timefile-filter file) or based on the privacy settings attached to 
# 	wall posts. 
#
# 	Created by Timothy Wright <spartas@gmail.com>
# 	Version: 1.0 [June 25th, 2011]
# 		* Stripped out hard-coded string values, to ready for publishing. 
# 		* Pulled out the hard-coded timestamp filter list into a user-specified external file.
# 		* Added (-P) privacy specifiers
# 		
# 		NOTE: BeautifulSoup and argparse may or may not be included with your Python distribution. This program 
# 					relies on both, and will not run without them.
#
# 	Version: 1.5 [July 3rd, 2011]
# 		* Factored out the logic for specifying privacy options, such that the user can choose which 
# 			privacy-level posts will show in the exported file. The default privacy level operates as before. 
# 			(-P option).
# 		* Support for hiding links to other pages using the -L option. By default, no additional links are hidden.
# 				Usage: "-L profile,friends"
# 		* Support for exporting pages other than the wall. NOTE: Currently the only pages with this support are 
# 			the wall and photos pages. By default, only the wall is exported. The -a options is used as follows:
# 				"-a wall,photos"
# 		* Added support for a config file, -f option, (either in addition to, or as an alternate to the timestamp 
# 			file). The config file is a JSON-structured file containing a single object, with string keys that this 
# 			script uses	for feature support. This script currently only recognizes two keys:
# 				1) "timefilter", another JSON-object that contains string keys and an array of timestamps to filter 
# 						from the wall page. The string keys within this object are ignored, they are useful for the user
# 						to specify groupings for the lists of timestamps.
#
# 				2) "albums", a JSON array containing names of the photo albums to filter from the photos page. Because 
# 					Facebook does not support exporting privacy levels for photo albums, this is the only way to control
# 					which photo albums are exported.
#
# 			See the included "config_filter.json" for example usage. NOTE: for JSON arrays and objects, be sure to 
# 			leave the comma (,) off the last element in the list, otherwise a JSON parsing error will occur.
#
# 		* The script now takes in the path to the "html" directory, and not simply the wall.html file. It will create
# 			a directory of the form html-%Y-%m-%d_%H_%M_%S, a timestamped html directory containing the timestamp when
# 			the script was run. If a file is specified, (i.e. wall.html, within the html directory), the parent 
# 			directory, "html" will be used. No alterations are made to the original "html" directory.
#
# 		* Restructured the script with functions to functional-ize some of the repeated processing. This is an area
# 			that will get improved in the future as well.
#
#
#
#
#
# 		NOTE: BeautifulSoup and argparse may or may not be included with your Python distribution. This program 
# 					relies on both, and will not run without them.

from BeautifulSoup import BeautifulSoup
from datetime import datetime
import sys
import re
import argparse
import os
import json
import shutil
import urllib

def list_timefilterfile_process( file_timeline_filter ):
	time_filter = []

	if( not os.path.isfile(file_timeline_filter)):
		print "The specified timeline filter file, %s, does not exist." % (args.timefile_filter)
		sys.exit(1)

	f = open(file_timeline_filter, 'r')

	for line in f:

		if( not re.match(re.compile('^\w*$'), line) and not re.match(re.compile('^\w*#'), line)):
			time_filter.append(line.strip())
	
	f.close()

	return time_filter


def extract_tab_links( bs, pages, suppressed_links ):
	tab_nav = bs.findAll(id="tabs")[0]
# 		* Factored out the logic for specifying privacy options, such that the user can choose which 
# 			privacy-level posts will show in the exported file. The default privacy operates as before. 
	for tab_link in tab_nav.findAll('a'):

		tab_name = tab_link['href'].split('.')[0]

		if( suppressed_links is not None and tab_name in suppressed_links ):
			tab_link.extract()
		elif( tab_name not in pages ):
			del(tab_link['href'])

def write_outfile( contents, outfilepath, filename ):
	outfile = open(os.path.join(outfilepath, filename), 'a')
	outfile.write( contents )
	outfile.close()

def process_wall( args, infilepath, outfilepath, time_filter ):

	# Add the timestamp-based wall filter options if specified (using -t or --timefile-filter)
	if(args.timefile_filter):
		file_timeline_filter = os.path.abspath(args.timefile_filter)
		time_filter.extend( list_timefilterfile_process(file_timeline_filter) )


	# For this to work properly, the local version of images must be installed in ../images/icons/
	# If this becomes unweildy, it may be necessary to put this into a separate file as well
	icon_map = {
		'http://photos-c.ak.fbcdn.net/photos-ak-snc1/v43/97/32061240133/app_2_32061240133_2659.gif' : 'youtube.gif',
	}

	infile = os.path.join(infilepath,'wall.html')

	if( not os.path.isfile(infile)):
		print "The input file specified, %s, does not exist." % (infile)
		sys.exit(1)

	f = open(infile, 'r')
	soup = BeautifulSoup( f.read() )
	f.close()

	profile_name = soup.find(id='rhs').find('h1').string

	# Do work

	# If "../images/icons" exists, assume that the user has or will download the necessary icon files from facebook,
	# otherwise, just leave the facebook.com links in
	if os.path.exists(os.path.join(infilepath,'..','images', 'icons')):

		icon_src_regex = re.compile('^http://www.facebook.com/images/icons/')

		# Root facebook.com icon image sources to the local filesystem (stop giving facebook.com traffic to analyze)
		for icon_image in soup.findAll('img', attrs={'class': 'icon'}, src=icon_src_regex):
			icon_image['src'] = re.sub(r'http://www.facebook.com/', '../', icon_image['src']); 
			

		# A future version will check that the corresponding files exist, and will download them if not
		for logo_img in icon_map:
			for icon_image in soup.findAll('img', attrs={'class': 'icon'}, src=logo_img):
				icon_image['src'] = re.sub(re.compile(logo_img), '../images/icons/' + icon_map[logo_img], icon_image['src'])


	## Remove links to other pages on the left-hand sidebar ##

	# Remove the profile photo link
	profile_image_link = soup.find(id='lhs').find('img').findParent('a')
	del(profile_image_link['href'])

	# Remove the tab links
	extract_tab_links(soup, args.pages, args.suppress_links)


	# Extract all 'class="profile"' tags
	class_profile = soup.findAll(attrs={'class':'profile'})

	# Remove all posts by anyone who is not the profile author
	for spantag in class_profile:
		if spantag.string != profile_name:
			spantag.parent.extract()

	# Remove all comments
	comments = soup.findAll(attrs={'class':'comments'})
	[comment.extract() for comment in comments]


	# Remove the explicit time entries, as specified above
	for timestr in time_filter:
		time_entry = soup.find(attrs={'class':'timerow'}, text=timestr)
		if( None == time_entry ):
			print "No entry found for time: %s" % (timestr)
		else:
			time_entry.findParent(attrs={'class':'feedentry'}).extract()


	# Remove "walllink" class posts (TEMPORARY, until a better solution can be found without exposing private data)
	wall_links = soup.findAll(attrs={'class':'walllink'})
	[wall_link.findParent(attrs={'class':'feedentry'}).extract() for wall_link in wall_links]


	### REMOVE PRIVATE POSTS ###

	privacy_opt_regex_map = {
		'x' 	: 'Except: ',
		'F' 	: 'Friends Only',
		'M' 	: 'Only Me',
		'o' 	: 'Friends of Friends',
		'E' 	: 'Everyone',
	}

	privacy_exceptions = []
	for privacy_specifier, regex in privacy_opt_regex_map.iteritems():
		if privacy_specifier in args.privacy:
			privacy_exceptions.extend( soup.findAll('img', attrs={'class':'privacy'}, title=re.compile(regex)) )

	[privacy_exception.findParent(attrs={'class':'feedentry'}).extract() for privacy_exception in privacy_exceptions]


	# Remove the privacy icons
	privacy_indicators = soup.findAll('img', attrs={'class':'privacy'})
	[privacy_indicator.extract() for privacy_indicator in privacy_indicators]


	# Strip out the download notice
	soup.find(attrs={'class':'downloadnotice'}).contents = ""

	# Write out the filtered wall page
	write_outfile(soup.prettify(), outfilepath, 'wall.html')


def process_photos( args, infilepath, outfilepath, album_filter ):

	infile = os.path.join(infilepath,'photos.html')

	if( not os.path.isfile(infile)):
		print "The input file specified, %s, does not exist." % (infile)
		sys.exit(1)

	f = open(infile, 'r')
	soup = BeautifulSoup( f.read() )
	f.close()


	## Remove links to other pages on the left-hand sidebar ##

	# Remove the profile photo link (We'll get better at handling this properly in the future based on
	# the absence/presence of the photos and the privacy of "Profile Pictures album)
	profile_image_link = soup.find(id='lhs').find('img').findParent('a')
	del(profile_image_link['href'])

	# Remove the tab links
	extract_tab_links(soup, args.pages, args.suppress_links)

	# Remove all comments
	comments = soup.findAll(attrs={'class':'comments'})
	[comment.extract() for comment in comments]


 	# Remove explicit albums, as specified in album_filter
	for albumstr in album_filter:
		soup.find('a', text=albumstr).findParent('div', attrs={'class':'album'}).extract()

	# Go over the remaining album pages and handle them as well
	for album_struct in soup.findAll('div', attrs={'class':'album'}):
		album_filename = urllib.url2pathname(album_struct.find('a')['href'])
		
		f = open(os.path.join(infilepath, album_filename), 'r')
		album_soup = BeautifulSoup( f.read() )
		f.close()

		process_album( album_soup, args, outfilepath, album_filename )

	# Strip out the download notice
	soup.find(attrs={'class':'downloadnotice'}).contents = ""

	# Write out the filtered photos page
	write_outfile(soup.prettify(), outfilepath, 'photos.html')


def process_album( soup, args, outfilepath, album_filename ):
	# Remove the tab links from album pages
	extract_tab_links(soup, args.pages, args.suppress_links)

	# Remove the profile photo link
	profile_image_link = soup.find(id='lhs').find('img').findParent('a')
	del(profile_image_link['href'])

	# Remove facebook.com links from the photo album timestamps
	album_fbk_regex = re.compile('^http://www.facebook.com/photo.php')
	for fbk_link in soup.findAll('a', href=album_fbk_regex):
		del(fbk_link['href'])

	# Remove all comments from album pages
	comments = soup.findAll(attrs={'class':'comments'})
	[comment.extract() for comment in comments]

	# Strip out the download notice
	soup.find(attrs={'class':'downloadnotice'}).contents = ""

	write_outfile( soup.prettify(), outfilepath, album_filename )



# Main()
if __name__ == "__main__":

	# Process arguments
	parser = argparse.ArgumentParser(description='Sanitize pages from a Facebook export file.')

	parser.add_argument('-a', '--pages', default="wall", 
			help='A comma-separated list of pages to process. Valid specifiers are profile,wall,photos,friends,notes,events,messages. The default is to only process the wall. Example usage: wall,photos')

	parser.add_argument('-L', '--suppress-links',
			help='A comma-separated list of page links remove from the left bar. Valid specifiers are profile,wall,photos,friends,notes,events,messages. The default is to hide nothing. Example usage: profile,friends,messages.')

	parser.add_argument('-P', '--privacy', default="xMF", 
			help='Specify the post privacy to filter out. Valid specifiers are E[x]cept: (Privacy Group), Only [M]e, [F]riends Only, Friends [o]f Friends, and [E]veryone. The default is xMF.')


	parser.add_argument('-t', '--timefile-filter', metavar='TIME_FILTER_FILE', 
			help='A file containing newline-separated time strings to filter from the feed wall')

	parser.add_argument('-f', '--filter-configfile', metavar='FILTER_FILE', 
			help='A JSON-structured file containing photo album names and an array of time strings to filter from the output')

	parser.add_argument('--version', action='version', version='%(prog)s 1.5')

	parser.add_argument('infile')

	args = parser.parse_args()


	valid_pages = ['profile', 'wall', 'photos', 'friends', 'notes', 'events', 'messages']
	pages = args.pages.split(',')

	# Default obj_config
	default_obj_config = obj_config = {
		"timefilter" : {},
		"albums" 		 : []
	}

	if(args.filter_configfile):
		file_configfile_filter = os.path.abspath(args.filter_configfile)

		if( not os.path.isfile(file_configfile_filter)):
			print "The specified config filter file, %s, does not exist." % (args.filter_configfile)
			sys.exit(1)

		configfile = open(file_configfile_filter, 'r')
		obj_config = json.load(open(file_configfile_filter, 'r'))
		configfile.close()

		# Re-generate the keys for un-specified values in the JSON config file
		for conf_key in default_obj_config:
			if conf_key not in obj_config:
				obj_config[conf_key] = default_obj_config[conf_key]

		temp_timefilter = []
		for k in obj_config['timefilter']:
			temp_timefilter.extend(obj_config['timefilter'][k])

		obj_config['timefilter'] = temp_timefilter
			

	for page in pages:
		if page not in valid_pages:
			print "Invalid page specified: %s" % (page)
			sys.exit(1)

	infile = os.path.abspath(args.infile)
	if( not os.path.exists(infile)):
		print "The input file specified, %s, does not exist." % (args.infile)
		sys.exit(1)

	file_path = os.path.abspath(args.infile)

	if os.path.isfile(file_path):
		file_path = os.path.dirname(file_path)

	str_outfile_dt = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
	outfile_path = os.path.join(os.path.dirname(file_path), os.path.basename(file_path) + "-" + str_outfile_dt)
	os.mkdir( outfile_path )

	# Copy 'style.css' to the target directory
	shutil.copy( os.path.join(file_path, 'style.css'), outfile_path)


	if "wall" in pages:
		process_wall(args, file_path, outfile_path, obj_config['timefilter'])
	if "photos" in pages:
		process_photos(args, file_path, outfile_path, obj_config['albums'])

	sys.exit(0)
