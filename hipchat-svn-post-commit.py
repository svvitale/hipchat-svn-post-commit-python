#!/usr/bin/python

# post-commit: Hook used for SVN post commits
#
# Scott Vitale
# svvitale@gmail.com

# This script is set to publish information after SVN commits to HipChat. 
#
# Required files/Application/services:
#     * Subversion: http://subversion.tigris.org/
#     * Working repository
#     * HipChat account and room setup: https://www.hipchat.com/
#     * HipChat token created: https://www.hipchat.com/groups/api
#
import os
import sys
import subprocess
import argparse
import urllib
import urllib2
import re
import json

# Set hipchat info
# These can be overridden by command line arguments
TOKEN="<token>"
ROOM="<room name>"
NAME="Subversion"

# svnlook location
LOOK="svnlook"

##############################################################
##############################################################
############ Edit below at your own risk #####################
##############################################################
##############################################################

def sendToHipChat( msg, token, room, name ):
	# replace newlines with XHTML <br />
	msg = msg.replace("\r", "").replace("\n", "<br />")

	# replace bare URLs with real hyperlinks
	msg = re.sub( r'(?<!href=")((?:https?|ftp|mailto)\:\/\/[^ \n]*)', r'<a href="\1">\1</a>', msg)

	# create request dictionary
	data = {
		'color': 'gray',
		'message': msg
	}
	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'Bearer ' + token
	}

	# urlencode and post
	req = urllib2.Request( 'https://api.hipchat.com/v2/room/' + room + '/notification', json.dumps( data ), headers )
	urllib2.urlopen( req ) 

# curl -H "Content-Type: application/json" https://api.hipchat.com/v2/room/NetRadius/notification?auth_token=O98vATcTCRgSFoAWpO0ByxfpGaRoIh0JfH0ba9Vv -d "{\"color\":\"green\",\"message\":\"Tetra Analytix: ${VERSION} has been deployed to the test environment\"}"
  
def runLook( *args ):
	# check_output will except if it fails so we don't spam the room with 'run svnlook help for help' messages
	return subprocess.check_output( ' '.join([LOOK] + list(args)), shell=True, stderr=subprocess.STDOUT)

def getCommitInfo( repo, revision ):
	comment = runLook("log", repo, "-r", revision)
	author = runLook("author", repo, "-r", revision)
	files = runLook("changed", repo, "-r", revision)

	chatMsg = ("""
[%s] %s committed revision %s
%s
Changed Files:
%s
""" % (repo, author.rstrip(), revision, comment, files)).strip()
  
	return chatMsg

def main():
	parser = argparse.ArgumentParser(description='Post commit hook that sends HipChat messages.')
	parser.add_argument('-r', '--revision', metavar='<svn rev>', required=True, help='SVN revision')
	parser.add_argument('-s', '--repository', metavar='<repository>', required=True, help='Repository to operate on')
	parser.add_argument('-t', '--token', metavar='<token>', required=False, help='HipChat authentication token', default=TOKEN)
	parser.add_argument('-o', '--room', metavar='<room>', required=False, help='HipChat room', default=ROOM)
	parser.add_argument('-n', '--name', metavar='<name>', required=False, help='HipChat name, default Subversion', default=NAME)

	args = parser.parse_args()
	
	chatMsg = getCommitInfo( args.repository, args.revision )
	sendToHipChat( chatMsg, args.token, args.room, args.name )

if __name__ == "__main__":
	main()
