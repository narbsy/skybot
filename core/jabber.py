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
        self.server = server
        self.nick = nick

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.parse_chat_message)
        self.out = Queue.Queue()  # responses from the server are placed here
        # format: [rawline, prefix, command, params, nick, user, host, paramlist, msg]

        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0199') # XMPP Ping

        self.connect()
        self.process(threaded=True)
        print ("done init.")
    
    def start(self, event):
        print("session start")
        self.getRoster()
        self.sendPresence()
        self.join(self.channel)

    def parse_chat_message(self, msg):
        if msg['mucnick'] == self.nick:
            return

        print("received: %s" % msg)

        self.out.put([msg.body, None, 'PRIVMSG', None, msg['mucnick'], msg['from'], None, [], None])
        
    def parse_invite(self, invite):
        pass

    def join(self, channel):
        print(channel)
        self.plugin['xep_0045'].joinMUC(channel, self.nick, wait=True)

    def msg(self, target, body):
        self.send_message(mto=target,mbody=body, mtype='groupchat')

    def set_nick(self, nick):
        # nick must be set before joining room
        pass

