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

from BeautifulSoup import BeautifulSoup
from datetime import datetime
import sys
import re
import argparse
import os

# Process arguments
parser = argparse.ArgumentParser(description='Sanitize the wall page from a Facebook export file.')

parser.add_argument('-P', '--privacy', default="xMF", 
		help='Specify the post privacy to filter out. Valid specifiers are E[x]cept: (Privacy Group), Only [M]e, [F]riends Only, Friends [o]f Friends, and [E]veryone. The default is xMF.')

parser.add_argument('infile')

parser.add_argument('-t', '--timefile-filter', metavar='FILTER_FILE', 
		help='A file containing newline-separated time strings to filter from the feed wall')

parser.add_argument('--version', action='version', version='%(prog)s 1.0')
args = parser.parse_args()


infile = os.path.abspath(args.infile)
if( not os.path.isfile(infile)):
	print "The input file specified, %s, does not exist." % (args.infile)
	sys.exit(1)

outfile_path = os.path.dirname(infile)


# Add the timestamp-based wall filter options if specified (using -t or --timefile-filter)
time_filter = []
if(args.timefile_filter):
	file_timeline_filter = os.path.abspath(args.timefile_filter)

	if( not os.path.isfile(file_timeline_filter)):
		print "The specified timeline filter file, %s, does not exist." % (args.timefile_filter)
		sys.exit(1)

	f = open(file_timeline_filter, 'r')

	for line in f:

		if( not re.match(re.compile('^\w*$'), line) and not re.match(re.compile('^\w*#'), line)):
			time_filter.append(line.strip())
	
	f.close()

# For this to work properly, the local version of images must be installed in ../images/icons/
# If this becomes unweildy, it may be necessary to put this into a separate file as well
icon_map = {
	'http://photos-c.ak.fbcdn.net/photos-ak-snc1/v43/97/32061240133/app_2_32061240133_2659.gif' : 'youtube.gif',
}

f = open(os.path.abspath(args.infile), 'r')
soup = BeautifulSoup( f.read() )
f.close()

profile_name = soup.find(id='rhs').find('h1').string

# Do work

# If "../images/icons" exists, assume that the user has or will download the necessary icon files from facebook,
# otherwise, just leave the facebook.com links in
if os.path.exists(os.path.join(outfile_path,'..','images', 'icons')):

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
tab_nav = soup.findAll(id="tabs")[0]
for tab_link in tab_nav.findAll('a'):
	del(tab_link['href'])



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
outfile_name = 'wall-%s.html' % (datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))

outfile = open(os.path.join(outfile_path, outfile_name), 'a')
outfile.write( soup.prettify() )
outfile.close();

