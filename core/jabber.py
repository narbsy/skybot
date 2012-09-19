import re
import time
import thread
import Queue
import sleekxmpp
import logging
import cgi
from xml.etree.cElementTree import XML, fromstring, tostring
logging.basicConfig()

class XMPP(sleekxmpp.ClientXMPP):
    "handles xmpp messages"
    def __init__(self, server, nick, port=5222, channels=[], conf={}):
        jid = conf.get('jid', nick)
        full_jid = '@'.join([jid, server])
        sleekxmpp.ClientXMPP.__init__(self, full_jid, conf.get('password'))

        self.channel = channels[0] or "skytest@conference." + server
        self.conf = conf
        self.host = server
        self.nick = nick
        self.escape = Escape()

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.parse_chat_message)
        self.out = Queue.Queue()  # responses from the server are placed here
        # format: [rawline, prefix, command, params, nick, user, host, paramlist, msg]

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0199') # XMPP Ping

        self.connect((server, port))
        self.process(threaded=True)
    
    def start(self, event):
        self.get_roster()
        self.send_presence()
        self.join(self.channel)

    def parse_chat_message(self, msg):
        if msg['mucnick'] == self.nick:
            return
       
        sent_by = msg['mucroom']
        if not sent_by:
            sent_by = msg['from']

        nick = msg['mucnick']
        if not nick:
            nick = str(sent_by)

        paramlist = [str(sent_by), msg['body']]
        lastparam = msg['body']

        self.out.put([msg['body'], None, 'PRIVMSG', msg['body'], nick, msg['from'], self.host, paramlist, lastparam])
        
    def join(self, channel):
        self.plugin['xep_0045'].joinMUC(channel, self.nick, wait=True)

    def msg(self, target, body):
        chat_type = 'chat'
        if target == self.channel:
            chat_type = 'groupchat'

        if not target.endswith(self.server):
            target = target + '@' + self.server

        html = XML(self.escape.html_escape(body)) 

        self.send_message(mto=target,mbody=self.escape.escape(body),mhtml=html, mtype=chat_type)

    def set_nick(self, nick):
        self.plugin['xep_0045'].leaveMUC(self.channel, self.nick)
        self.nick = nick
        self.join(self.channel)
    
    @property
    def server(self):
        return self.host

class Escape(object):
    escape_bold_re = re.compile(r'\x02(.*?)\x02')

    def boldify(self, matchobj):
        return ''.join(['<b>', matchobj.group(1), '</b>'])

    def escape(self, msg):
        return msg.replace('\x02', '*')
          
    def html_escape(self, msg):
        body = re.sub(self.escape_bold_re, self.boldify, msg) 
        return ''.join(['<body>', body, '</body>'])
    
