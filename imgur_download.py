import sys
import re
import urllib.request
import urllib.parse
import urllib.error
import urllib
import os
import string
import random
import time
import argparse

parser = argparse.ArgumentParser(description='Download images from reddit')
parser.add_argument("-l", help="Log number of downloaded files", action="store_true")
args = parser.parse_args()

home = os.getenv("HOME")
downloaded = '{0}/.config/imgur_down/downloaded.txt'.format(home)
SUBREDDITS = '{0}/.config/imgur_down/subreddits.txt'.format(home)
logfile = '{0}/.config/imgur_down/log.txt'.format(home)
download_dir = '{0}/Pictures/Imguralbums'.format(home)

imgur_albums_count = 0
picture_links_count = 0
gif_links_count = 0

# The pid for the lock file
pid = str(os.getpid())
pidfile = "/tmp/rid.pid"


def pid_exists(pid):
    try:
        os.kill(int(pid), 0)
        return False
    except OSError:
        return True


def image_down(url, ext):
    try:
        urllib.request.urlretrieve(url, download_dir + '/' + i + '/' + time.strftime('%Y_%m_%d_%H_%M_%S') + ext)
    except urllib.error.URLError:
        print("WARNING: There was an exception downloading from a direct link (likely a 403 or 404)\n")
        pass

# If the lock file exists we exit
if os.path.isfile(pidfile):
    if pid_exists(open(pidfile).read()) is True:
        print("Found stale lockfile, removing")
        os.unlink(pidfile)
    elif pid_exists(open(pidfile).read()) is False:
        print("{0} already exists, exiting".format(pidfile))
        sys.exit()
    else:
        print('Unable to write lockfile')
        sys.exit()

with open(pidfile, mode='w') as f:
    f.write(str(pid))

with open(SUBREDDITS) as f:
    lines = f.read().splitlines()
    print(lines)
for i in lines:
    reddit_url = "https://reddit.com/r/{0}.json".format(i)
    req = urllib.request.Request(reddit_url,
    #The user-agent we send so we don't get massively limited
    headers={'User-Agent': "AbotbyATGUNAT"})
    print('Checking: {0}'.format(i))
    reddit_call = urllib.request.urlopen(req)
    result = reddit_call.read().decode('utf-8')
    # https?://https?://m?.?imgur.com/a......
    results = re.findall('https?://m?.?imgur.com/a......', result)
    for image_url in results:
        os.makedirs('{0}/{1}'.format(download_dir, i), exist_ok=True)
        os.chdir('{0}/{1}'.format(download_dir, i))
        if image_url not in open(downloaded).read():
            os.system('imgurdl {0}'.format(image_url))
            imgur_albums_count = imgur_albums_count + 1
            # We write the downloaded url to a file so we can quickly skip already downloaded files
            f = open(downloaded, 'a')
            f.write(image_url + '\n')
            f.close()
    # We remove qoutes so the urls aren't qouted
    result = result.replace('"', '')
    # This regex is from https://stackoverflow.com/questions/169625/regex-to-check-if-valid-url-that-ends-in-jpg-png-or-gif
    direct_links = re.findall('https?://(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpg|gif|png|jpeg|gifv)', result)
    # This regex with get all links to gfycat
    gfycat_links = re.findall('https?://gfycat.com/\w*', result)
    for gfy_links in gfycat_links:
        char_set = string.ascii_uppercase + string.digits
        # We need to get the mp4 from the link. We get the mp4 and not the gif to save on bandwidth
        # We need to request the mp4 from *.gfycat.com instead of gfycat.com
        down_gfy_link = gfy_links.replace('gfycat.com', 'giant.gfycat.com')
        # This chanages http to https
        down_gfy_link = down_gfy_link.replace('http://', 'https://')
        down_gfy_link = down_gfy_link + '.mp4'
        if gfy_links not in open(downloaded).read():
            print('Downloading\n      {0} in {1}/{2} as {3} \n'.format(down_gfy_link, download_dir, i, time.strftime('%Y_%m_%d_%H_%M_%S')))
            try:
                urllib.request.urlretrieve(down_gfy_link, download_dir + '/' + i + '/' + time.strftime('%Y_%m_%d_%H_%M_%S') +'.mp4')
                gif_links_count = gif_links_count + 1
            except urllib.error.URLError:
                print("WARNING: There was an exception downloading from gfycat (likely a 403 or 404)\n")
                try:
                    # Here we try to use the fat.gfycat.com server instead of the giant.gfycat.com. For some reason we get a
                    # 403 if we use the wrong one when we try the mp4
                    down_gfy_link = down_gfy_link.replace('giant', 'fat')
                    print('Trying fat.gfycat.com\n')
                    print('Downloading\n      {0} in {1}/{2} as {3} \n'.format(down_gfy_link, download_dir, i, time.strftime('%Y_%m_%d_%H_%M_%S')))
                    urllib.request.urlretrieve(down_gfy_link, download_dir + '/' + i + '/' + time.strftime('%Y_%m_%d_%H_%M_%S') + '.mp4')
                    gif_links_count = gif_links_count + 1
                except urllib.error.URLError:
                    # I'm not going to code all the back up servers right now because tracking them all down is a pain
                    print('fat.gfycat failed\n')
                    pass
            print('Done!\n\n')
            f = open(downloaded, 'a')
            f.write(gfy_links + '\n')
            f.close()
    for d_image_url in direct_links:
        # os.system("mkdir -p " + home + "/Pictures/Imguralbums/" + i)
        os.makedirs('{0}/Pictures/Imguralbums/{1}'.format(home, i), exist_ok=True)
        # The d_image_url not in open(downloaded).read() is what keeps this from redownloading images
        # This stops us from downloading (some) thumbnails
        # TODO clean this up.
        if not re.findall('https?://i.redditmedia.com/............................................jpg', d_image_url) and not re.findall('https?://..thumbs.redditmedia.com/............................................jpg', d_image_url) and d_image_url not in open(downloaded).read():
            print('Downloading\n     {0} in {1}/{2} as {3}\n'.format(d_image_url, download_dir, i, time.strftime('%Y_%m_%d_%H_%M_%S')))
            if '.' in d_image_url[-4:] and bool(re.search('https?://i.imgur.com/\w*.gif', d_image_url)) == False:
                image_down(d_image_url, d_image_url[-4:])
                picture_links_count = picture_links_count + 1
            elif '.' in d_image_url[-4:] and bool(re.search('https?://i.imgur.com/\w*.gif', d_image_url)) == True:
                # This checks if the gif is coming from imgur. If it is we change it from gif to mp4 to save on bandwidth
                try:
                    d_image_url = d_image_url.replace('.gif', '.mp4')
                    image_down(d_image_url, '.mp4')
                    d_image_url = d_image_url.replace('.mp4', '.gif')

                except urllib.error.URLError:
                    print("WARNING: There was an exception downloading from a direct link (likely a 403 or 404)\n")
                    pass
            elif '.' in d_image_url[-5:]:
                image_down(d_image_url, d_image_url[-5:])
                picture_links_count = picture_links_count + 1
            print('Done\n')
            # We need to added downloaded urls to the list so we don't redownload them
            f = open(downloaded, 'a')
            f.write(d_image_url + '\n')
            f.close()
for i in lines:
    if os.path.isdir('{0}/{1}'.format(download_dir, i)) == True:
        pass
    elif os.path.isdir(download_dir + '/' + i) == False:
        print('WARNING: {0}/{1} does not exist\nExiting'.format(download_dir, i))
        sys.exit()
    os.chdir('{0}/{1}'.format(download_dir, i))
    # We use system calls instead of a zip lib because of laziness
    # TODO change to zip lib so this can run on windows
    os.system('for i in */; do zip -r "${i%/}.cbz" "$i" -x *.cbr; done')
    os.system('rm -r */')
print('Done!')
total = picture_links_count + gif_links_count + imgur_albums_count
if args.l:
    date_finished = time.strftime("[%d/%m/%Y_%H:%M:%S]")
    with open(logfile, mode='a') as log:
        print(date_finished + '\nDownloaded:\n{0} Pictures\n{1} Gyfs\n{2} Imgur Albums\n{3} Total items downloaded'.format(picture_links_count, gif_links_count, imgur_albums_count, total), file=log)
print('''Downloaded:\n
{0} Pictures\n
{1} Gyfs\n
{2} Imgur Albums\n
{3} Total items downloaded\n'''.format(picture_links_count, gif_links_count, imgur_albums_count, total))

# We remove the pid file
os.unlink(pidfile)
