# coding: utf-8
import json, sys, logging

from cookielib import CookieJar
from urlparse import urljoin
from urllib import urlencode
from urllib2 import *
from re import findall

ERROR_DELAY = 5

APP_ID = '4152748'
SCOPE = 'messages'

INVALID_METHOD_ERROR = 3
INVALID_TOKEN_ERROR = 5
PERMISSIONS_ERROR = 7
GROUP_BLOCKED_ERROR = 15
NO_ERROR = 200

opener = build_opener(
         HTTPCookieProcessor(CookieJar()),
         HTTPRedirectHandler())
install_opener(opener)

log = logging.getLogger('wallChecker')

class Api(object):
	def __init__(self, login, password):
		self.login = login
		self.password = password

		self.token = ''
		self.getToken()
	
	def auth(self):
		html = urlopen('https://oauth.vk.com/oauth/authorize?'
						'redirect_uri=https://oauth.vk.com/blank.html'
						'&response_type=token'
						'&client_id=' + APP_ID +\
						'&scope=' + SCOPE +\
						'&display=page'
						'&v=5.16').read()

		ip_h = findall('name="ip_h" value="(\w+)"', html)[0]
		to = findall('name="to" value="([^"]+)"', html)[0]

		data = urlencode({
			'email': self.login,
			'pass': self.password,
			'_origin': 'http://oauth.vk.com',
			'ip_h': ip_h,
			'to': to
		})
		
		resp = urlopen('https://login.vk.com/?act=login&soft=1&utf8=1', data)
		
		return resp
	
	def getToken(self):
		log.info('Getting token')
		
		resp = self.auth()
		
		try: # Redirected to get permissions
			url = findall('method="post" action="([^"]+)"', resp.read())[0]
			url = urljoin('https://vk.com', url)

			redirectUrl = urlopen(url, urlencode({'submit': 'Allow'})).geturl()
			
		except IndexError: #  Already got permissions
			redirectUrl = resp.geturl()
		
		try:
			self.token = findall('access_token=(\w+)', redirectUrl)[0]
		except IndexError:
			sys.exit('Invalid login/password')

		return self.callMethod('check') # Checking token
	
	def callMethod(self, methodName, params = {}):	
		while 1:
			try:
				if methodName != 'check':
					log.info('Calling method %s' %(methodName))
				else:
					log.info('Checking token')
				
				resp = urlopen('https://api.vk.com/method/%s?%s&access_token=%s' 
								%(methodName, urlencode(params.items()), self.token)).read()
				
				error = self.checkError(resp)
				errorCode = error[0]
				errorMessage = error[1]
				
				if errorCode == NO_ERROR:
					break
					
				elif errorCode == INVALID_TOKEN_ERROR:
					if methodName != 'check':
						log.warn('Invalid token. Trying to get new')
						self.getToken()
					else:
						return 0
						
					continue
					
				elif errorCode == INVALID_METHOD_ERROR:
					if methodName != 'check':
						log.error('Invalid method called')
						sys.exit(INVALID_METHOD_ERROR)
					else:
						log.info('Token is valid')
						
					return 1
					
				elif errorCode == PERMISSIONS_ERROR:
					log.error('Not enough permissions')
					sys.exit(PERMISSIONS_ERROR)
					
				elif errorCode == GROUP_BLOCKED_ERROR:
					return GROUP_BLOCKED_ERROR
				
				else:
					raise Exception('Error %d: %s' %(errorCode, errorMessage))
			except Exception, err:  
				log.error(str(err))

                sleep(ERROR_DELAY)
		
		return json.loads(resp)['response']
		
	def checkError(self, resp):
		if 'error' in resp:
			info = json.loads(resp)['error']
			return (info['error_code'], info['error_msg'])
		return (NO_ERROR, '')
	
	def sendMessage(self, domain = 'diana.makina', message = '', attachment = ''):
		self.callMethod('messages.send', 
										{
											'domain': domain,
											'message': message,
											'attachment': attachment
										})
	
	def getPostsList(self, gid, count = 5):
		resp = self.callMethod('wall.get', 
										{
											'owner_id': '-%s' %(gid),
											'count': count,
											'filter': 'others'
										})
		
		if resp != GROUP_BLOCKED_ERROR:
			return resp[1:] # resp[0] - number of posts
		else:
			return []
		
	def getGroupsList(self):
		return self.callMethod('groups.get')
