import re
import time
import thread
import Queue
import sleekxmpp
import logging
logging.basicConfig()

class XMPP(sleekxmpp.ClientXMPP):
    "handles Jabber communication protocol"
    def __init__(self, server, nick, port=6667, channels=[], conf={}):
        jid = '@'.join([nick, server])
        sleekxmpp.ClientXMPP.__init__(self, jid, 'test')

        self.channel = channels[0] or "skytest@conference." + server
        self.conf = conf
        self.host = server
        self.nick = nick

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.parse_chat_message)
        self.out = Queue.Queue()  # responses from the server are placed here
        # format: [rawline, prefix, command, params, nick, user, host, paramlist, msg]

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0199') # XMPP Ping

        self.connect()
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
        
    def parse_invite(self, invite):
        pass

    def join(self, channel):
        self.plugin['xep_0045'].joinMUC(channel, self.nick, wait=True)

    def msg(self, target, body):
        chat_type = 'chat'
        if target == self.channel:
            chat_type = 'groupchat'

        self.send_message(mto=target,mbody=body, mtype=chat_type)

    def set_nick(self, nick):
        # nick must be set before joining room
        pass
    
    @property
    def server(self):
        return self.host

