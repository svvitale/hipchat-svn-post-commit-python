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

# Set hipchat info
#
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
	request = {
		'auth_token': token,
		'room_id': room,
		'from': name,
		'message': msg,
		'notify': 1,
	}

	# urlencode and post
	urllib2.urlopen( "https://api.hipchat.com/v1/rooms/message", urllib.urlencode( request ) )
  
def runLook( subcmd, *args ):
	p = subprocess.Popen([LOOK, subcmd] + list(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return p.communicate()[0].strip()

def getCommitInfo( repo, revision ):
	comment = runLook("log", repo, "-r", revision)
	author = runLook("author", repo, "-r", revision)
	files = runLook("changed", repo, "-r", revision)

	chatMsg = ("""
%s committed revision %s
%s
""" % (author, revision, comment)).strip()
  
	return chatMsg

def main():
	parser = argparse.ArgumentParser(description='Post commit hook that sends HipChat messages.')
	parser.add_argument('-r', '--revision', metavar='<svn rev>', required=True, help='SVN revision')
	parser.add_argument('-s', '--repository', metavar='<repository>', required=True, help='Repository to operate on')

	args = parser.parse_args()
	
	chatMsg = getCommitInfo( args.repository, args.revision )
	sendToHipChat( chatMsg, TOKEN, ROOM, NAME )

if __name__ == "__main__":
	main()
