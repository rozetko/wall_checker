# coding: utf-8
import sys, os, logging

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

RECENT_POSTS = ConfigParser()

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
                RECENT_POSTS.read('recent_posts') # Updating ConfigParser instance
                try:
                        groupsList = api.getGroupsList()                
                        groupsAmount = len(groupsList)
                                                
                        for i, group in enumerate(groupsList, 1):
                                gid = str(group)
                                
                                log.info('%d/%d (club%s)' %(i, groupsAmount, gid))
                                
                                postsList = api.getPostsList(gid)

                                recentPosts = getRecentPosts(gid, postsList)

                                if recentPosts:
                                        log.info('%d new posts\n' %(len(recentPosts)))
                                
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
                        
        updateRecentPostTime(gid, postsList[0]['date'])
                
        return recentPosts
        
def getLastPostTime(gid):
        if RECENT_POSTS.has_option('groups', gid):
                return RECENT_POSTS.getint('groups', gid)
        
        updateRecentPostTime(gid, int(time() - ACTUAL_TIME))

        return int(time() - ACTUAL_TIME)
                        
def updateRecentPostTime(gid, lastPostTime):
        RECENT_POSTS.set('groups', gid, lastPostTime)
        with open('recent_posts', 'w') as f:
                RECENT_POSTS.write(f)

if __name__ == '__main__':
        main()
