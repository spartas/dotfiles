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
# 	Version 1.6 [September 5th, 2011]
# 		* Facebook changed the "Everyone" privacy value to "Public". "E" may still be used to specify "[E]veryone", 
# 			but it's been updated to use "Public". "P" has been added to support "[P]ublic as well.
# 		* Facebook appears to be using the hCard microformat in class names, so I've had to update the script to use
# 			these as well.
#
# 	Version 2.0 [September 18th, 2011]
# 		* Major changes to the infile. Now, the infile argument takes the raw facebook zip export file, rather than 
# 			requiring the user to extract it. Backwards compatibility is not provided. In previous versions, this 
# 			script operated on the "wall.html" and "html" infile arguments, in 1.0 and 1.5, respectively. This version
# 			operates on the zip export file itself.
# 			
# 		* Supports reading configuration options from a ".fbk" directory (within the user's home directory. Future 
# 			versions may allow a command-line option for specifying an arbitrary location for this directory. 
# 			Command-line options will supercede any files within this directory. 
# 				* Within this config directory, a "config_filter.json" file will automatically be used if it exists. 
# 				* If a style.css file exists, it will be copied into the output directory (otherwise the one within the
# 					zip file will be used).
#
# 		* Cleaned up the argument lists for non-modified variables within helper processing functions.
#
#
# 		NOTE: BeautifulSoup and argparse may or may not be included with your Python distribution. This program 
# 					relies on both, and will not run without them.

from BeautifulSoup import BeautifulSoup
import zipfile
from zipfile import ZipFile
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


def zipfile_copy( zipfile, src_path, dest_path ):
	file_src = zipfile.open( src_path )
	file_target = file(dest_path, 'wb')

	shutil.copyfileobj( file_src, file_target )

	file_src.close()
	file_target.close()


def process_wall( zip_infile, outfilepath, time_filter ):

	# Add the timestamp-based wall filter options if specified (using -t or --timefile-filter)
	if(args.timefile_filter):
		file_timeline_filter = os.path.abspath(args.timefile_filter)
		time_filter.extend( list_timefilterfile_process(file_timeline_filter) )


	# For this to work properly, the local version of images must be installed in ../images/icons/
	# If this becomes unweildy, it may be necessary to put this into a separate file as well
	icon_map = {
		'http://photos-c.ak.fbcdn.net/photos-ak-snc1/v43/97/32061240133/app_2_32061240133_2659.gif' : 'youtube.gif',
	}

	f = zip_infile.open('%s/html/wall.html' % (basedirname), 'r')
	soup = BeautifulSoup( f.read() )
	f.close()

	profile_name = soup.find(id='rhs').find('h1').string

	# Do work

	# If "[config_dir]/images/icons" exists, assume that the user has or will download the necessary icon files from 
	#	facebook, otherwise, just leave the facebook.com links in
	if ( use_configdir and os.path.exists(os.path.join(config_dir,'images', 'icons')) ):

		icon_src_regex = re.compile('^http://www.facebook.com/images/icons/')

		# Root facebook.com icon image sources to the local filesystem (stop giving facebook.com traffic to analyze)
		for icon_image in soup.findAll('img', attrs={'class': attr_classname_map['profile']['icon']}, src=icon_src_regex):
			icon_image['src'] = re.sub(r'http://www.facebook.com/', '../', icon_image['src']); 
			

		# A future version will check that the corresponding files exist, and will download them if not
		for logo_img in icon_map:
			for icon_image in soup.findAll('img', attrs={'class': attr_classname_map['profile']['icon']}, src=logo_img):
				icon_image['src'] = re.sub(re.compile(logo_img), '../images/icons/' + icon_map[logo_img], icon_image['src'])


	## Remove links to other pages on the left-hand sidebar ##

	# Remove the profile photo link
	profile_image_link = soup.find(id='lhs').find('img').findParent('a')
	del(profile_image_link['href'])

	# Remove the tab links
	extract_tab_links(soup, args.pages, args.suppress_links)


	# Extract all 'class="profile"' tags
	class_profile = soup.findAll(attrs={'class': attr_classname_map['profile']['profile']})

	# Remove all posts by anyone who is not the profile author
	for spantag in class_profile:
		if spantag.string != profile_name and None == spantag.findParent(attrs={'class' : attr_classname_map['profile']['comments']}):
			spantag.findParent(attrs={'class':attr_classname_map['profile']['feedentry']}).extract()

	# Remove all comments
	comments = soup.findAll(attrs={'class': attr_classname_map['profile']['comments']})
	[comment.extract() for comment in comments]


	# Remove the explicit time entries, as specified above
	for timestr in time_filter:
		time_entry = soup.find(attrs={'class': attr_classname_map['profile']['timerow']}, text=timestr)
		if( None == time_entry ):
			print "No entry found for time: %s" % (timestr)
		else:
			time_entry.findParent(attrs={'class': attr_classname_map['profile']['feedentry']}).extract()


	# Remove "walllink" class posts (TEMPORARY, until a better solution can be found without exposing private data)
	wall_links = soup.findAll(attrs={'class': attr_classname_map['profile']['walllink']})
	[wall_link.findParent(attrs={'class': attr_classname_map['profile']['feedentry']}).extract() for wall_link in wall_links]


	### REMOVE PRIVATE POSTS ###

	privacy_opt_regex_map = {
		'x' 	: 'Except: ',
		'F' 	: 'Friends Only',
		'M' 	: 'Only Me',
		'o' 	: 'Friends of Friends',
		'E' 	: 'Public',
		'P' 	: 'Public',
	}

	privacy_exceptions = []
	for privacy_specifier, regex in privacy_opt_regex_map.iteritems():
		if privacy_specifier in args.privacy:

			img_privacy = soup.findAll('img', attrs={'class': attr_classname_map['profile']['privacy']}, title=re.compile(regex))
			privacy_exceptions.extend( img_privacy )


	[privacy_exception.findParent(attrs={'class': attr_classname_map['profile']['feedentry']}).extract() for privacy_exception in privacy_exceptions]


	# Remove the privacy icons
	privacy_indicators = soup.findAll('img', attrs={'class': attr_classname_map['profile']['privacy']})
	[privacy_indicator.extract() for privacy_indicator in privacy_indicators]


	# Strip out the download notice
	soup.find(attrs={'class': attr_classname_map['profile']['downloadnotice']}).contents = ""

	# Write out the filtered wall page
	write_outfile(soup.prettify(), outfilepath, 'wall.html')


def process_photos( zip_infile, outfilepath, album_filter ):

	f = zip_infile.open('%s/html/photos.html' % (basedirname), 'r')
	soup = BeautifulSoup( f.read() )
	f.close()


	## Remove links to other pages on the left-hand sidebar ##

	# Remove the profile photo link (We'll get better at handling this properly in the future based on
	# the absence/presence of the photos and the privacy of "Profile Pictures album)
	profile_image_link = soup.find(id='lhs').find('img').findParent('a')
	del(profile_image_link['href'])

	# Remove the tab links
	extract_tab_links(soup, args.pages, args.suppress_links)

	# ADDITION: 2011-09-05
	# This is necessary because BS can choke on photo album comments. So we'll remove them individually first and
	# then do the default action of removing the whole comment block as before.
	comments = soup.findAll(attrs={'class': 'comment hentry'})
	[comment.extract() for comment in comments]
	# END ADDITION

	# Remove all comments
	comments = soup.findAll(attrs={'class': attr_classname_map['photos']['comments']})
	[comment.extract() for comment in comments]


 	# Remove explicit albums, as specified in album_filter
	for albumstr in album_filter:
		soup.find('a', text=albumstr).findParent('div', attrs={'class': attr_classname_map['photos']['album']}).extract()

	# Go over the remaining album pages and handle them as well
	for album_struct in soup.findAll('div', attrs={'class': attr_classname_map['photos']['album']}):
		album_filename = urllib.url2pathname(album_struct.find('a')['href'])
		
		f = open(os.path.join('%s/html/' % (basedirname), album_filename), 'r')
		album_soup = BeautifulSoup( f.read() )
		f.close()

		process_album( album_soup, outfilepath, album_filename )

	# Strip out the download notice
	soup.find(attrs={'class': attr_classname_map['photos']['downloadnotice']}).contents = ""

	# Write out the filtered photos page
	write_outfile(soup.prettify(), outfilepath, 'photos.html')


def process_album( soup, outfilepath, album_filename ):
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
	comments = soup.findAll(attrs={'class': attr_classname_map['photos']['comments']})
	[comment.extract() for comment in comments]

	# Strip out the download notice
	soup.find(attrs={'class': attr_classname_map['photos']['downloadnotice']}).contents = ""

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

	parser.add_argument('infile', help='The export zip file to process.')

	args = parser.parse_args()

	config_dir = os.path.join( os.path.expanduser('~'), '.fbk' )
	use_configdir = os.path.exists( config_dir )

	valid_pages = ['profile', 'wall', 'photos', 'friends', 'notes', 'events', 'messages']
	pages = args.pages.split(',')

	# Default obj_config
	default_obj_config = obj_config = {
		"timefilter" : {},
		"albums" 		 : []
	}

	
	file_configfile_filter = None
	if(args.filter_configfile):
		file_configfile_filter = os.path.abspath(args.filter_configfile)
	elif( use_configdir and os.path.exists(os.path.join(config_dir, 'config_filter.json'))):
		file_configfile_filter = os.path.join(config_dir, 'config_filter.json')

	if(file_configfile_filter):

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

	if( not zipfile.is_zipfile(infile) ):
		print "The input file specified, %s, is not a valid zip file." % (args.infile)
		sys.exit(1)

	# Open the zip file for reading, and figure out the base filename
	file_path = os.path.abspath(args.infile)
	zip_infile = zipfile.ZipFile( file_path, 'r' )
	basedirname = zip_infile.namelist()[0].split('/')[0]

	# Create the base filename (if it doesn't exist)
	if( not os.path.exists(os.path.join(os.path.dirname(file_path), basedirname)) ):
		if( not os.path.exists(os.path.join(os.path.dirname(file_path), basedirname)) ):
			os.mkdir( os.path.join(os.path.dirname(file_path), basedirname) )
		
	# Set up the date-stampped html directory
	str_outfile_dt = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
	outfile_path = os.path.join(os.path.dirname(file_path), basedirname, "html-" + str_outfile_dt)
	os.mkdir( outfile_path )

	# Copy 'style.css' to the target directory
	if( use_configdir and os.path.isfile(os.path.join(config_dir, 'style.css')) ):
		shutil.copy( os.path.join(config_dir, 'style.css'), outfile_path)
	else:
		zipfile_copy( zip_infile, '%s/html/style.css' % (basedirname), os.path.join(outfile_path, 'style.css') )


	attr_classname_map = {
		'profile' : {
			'album' 					: 'album',
			'comments' 				: 'comments hfeed',
			'downloadnotice' 	: 'downloadnotice',
			'feedentry' 			: 'feedentry hentry',
			'icon' 						: 'icon',
			'privacy' 				: 'privacy',
			'profile' 				: 'profile fn',
			'timerow' 				: 'timerow',
			'walllink' 				: 'walllink',
		},
		'photos' : {
			'album' 					: 'album',
			'comments' 				: 'comment hentry',
			'downloadnotice' 	: 'downloadnotice',
		},
	}


	if "wall" in pages:
		process_wall(zip_infile, outfile_path, obj_config['timefilter'])
	if "photos" in pages:
		process_photos(zip_infile, outfile_path, obj_config['albums'] )

	zip_infile.close()

	sys.exit(0)
