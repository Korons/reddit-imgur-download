import sys
import re
import urllib.request, urllib.parse, urllib.error, urllib
import os
import time
home = os.getenv("HOME")
downloaded = home + '/.config/imgur_down/downloaded.txt'
SUBREDDITS = home + '/.config/imgur_down/subreddits.txt'
logfile = home + '/Pictures/Imguralbums/log.txt'
with open(SUBREDDITS) as f:
	lines = f.read().splitlines()
	print (lines)
for i in lines:
	url = "https://reddit.com/r/" + i + ".json"
	req = urllib.request.Request(
    url, 
    # The user-agent we send so we don't get massively limited
    headers={'User-Agent': "abotbyATGUNAT"}
	)
	print (url)
	reddit_call = urllib.request.urlopen(req)
	result = reddit_call.read().decode('utf-8')
	results = re.findall('https?://imgur.com/a......', result)
	direct_links = re.findall('https?:\/\/.*.png', result)
	print (direct_links)
	for image_url in results:
		# This can and should be changed to a os.mkdir
		os.system("mkdir -p /home/wil/Pictures/Imguralbums/" + i)
		os.chdir("/home/wil/Pictures/Imguralbums/" + i)
		if image_url not in open(downloaded).read():
			os.system("imgurdl " + image_url)
			# We write the downloaded url to a file so we can quickly skip already downloaded files
			f = open(downloaded,'a')
			f.write(image_url + '\n')
			f.close() 
for i in lines:
	os.chdir(home + "/Pictures/Imguralbums/" + i)
	# These system calls seem to hang the program some times no idea why
	os.system('for i in */; do zip -r "${i%/}.cbr" "$i" -x *.cbr; done')
	os.system('rm -r */')
	# Logging 
	time = time.strftime("%H:%M:%S:%d/%m/%Y")
	f = open(logfile,'r+')
	f.write(("Ran at " + time))
	f.close

