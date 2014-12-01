# coding: utf-8
import sys, os, logging, json

from api import Api
from time import sleep, time
from datetime import datetime
from ConfigParser import ConfigParser
from optparse import OptionParser
from gui import Gui

WINDOWS = 'nt'

MESSAGE_DELAY = 1
CHECK_DELAY = 1
ERROR_DELAY = 5

ACTUAL_TIME = 60 * 60 # 1st number - minutes

class RecentPosts(object):
        def __init__(self):
                self.filename = 'recent_posts.json'
                self.update()

        def update(self):
                try:
                        with open(self.filename, 'r') as f:
                                self.posts = json.load(f)
                except (ValueError, IOError):
                        with open(self.filename, 'w') as f: # Create file
                                f.write('{}')

        def set(self, gid, time):
                self.posts[gid] = time
                with open(self.filename, 'w') as f:
                        json.dump(self.posts, f, indent = 4)

        def get(self, gid):
                try:
                        return self.posts[gid]
                except KeyError:
                        return 0
                

def main():
        if os.name == WINDOWS:
                gui = Gui()
                login = gui.result[0]
                password = gui.result[1]
        else:
                parser = OptionParser(usage = 'usage: %prog login password')
                
                (options, args) = parser.parse_args()

                if len(args) != 2:
                        parser.error("wrong number of arguments")

                login = args[0]
                password = args[1]

        log = logging.getLogger('wallChecker')
        log.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler('log.log')
        streamHandler = logging.StreamHandler()

        fileHandler.setLevel(logging.WARNING)
        streamHandler.setLevel(logging.DEBUG)

        fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        streamHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        log.addHandler(fileHandler)
        log.addHandler(streamHandler)
        
        api = Api(login = login, password = password)
        
        while 1:
                RECENT_POSTS.update()
                try:
                        groupsList = api.getGroupsList()                
                        groupsAmount = len(groupsList)
                                                
                        for i, group in enumerate(groupsList, 1):
                                gid = str(group)
                                
                                log.info('%d/%d (club%s)' %(i, groupsAmount, gid))
                                
                                postsList = api.getPostsList(gid)

                                recentPosts = getRecentPosts(gid, postsList)

                                if recentPosts:
                                        log.info('%d new posts' %(len(recentPosts)))
                                
                                for post in recentPosts:
                                        api.sendMessage(attachment = post)
                                        sleep(MESSAGE_DELAY)
                                sleep(CHECK_DELAY)
                                
                except KeyboardInterrupt:
                        sys.exit()
                except Exception, err:
                        log.error(err)
                        
                        sleep(ERROR_DELAY)
   
def getRecentPosts(gid, postsList):
        if not postsList:
                return []
        
        lastPostTime = getLastPostTime(gid)

        recentPosts = []
                        
        for post in postsList:
                postTime = int(post['date'])
                
                if postTime > lastPostTime and postTime >= time() - ACTUAL_TIME:
                        recentPosts.append('wall-%s_%s' %(gid, post['id']))
                else:
                        break
                        
        RECENT_POSTS.set(gid, postsList[0]['date'])
                
        return recentPosts
        
def getLastPostTime(gid):
        if RECENT_POSTS.get(gid):
                return int(RECENT_POSTS[gid])
        
        RECENT_POSTS.set(gid, int(time() - ACTUAL_TIME))

        return int(time() - ACTUAL_TIME)


if __name__ == '__main__':
        global RECENT_POSTS
        RECENT_POSTS = RecentPosts()

        main()
