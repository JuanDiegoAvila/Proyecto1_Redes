from slixmpp import *
from slixmpp import exceptions
import logging
import sys
import asyncio
import xmpp
import ssl

ssl.match_hostname = lambda cert, hostname: True

SERVER = "alumchat.xyz"

logging.basicConfig(level=logging.DEBUG, filename='debug_log.txt')

if sys.platform == 'win32' and sys.version_info >= (3, 8):
     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Client(ClientXMPP):

    def __init__(self, jid, password):
        super(Client, self).__init__(jid, password)

        self.add_event_handler("session_start", self.conectar)
        self.add_event_handler("message", self.mensaje)
        self.add_event_handler("register", self.registrar_usuario)

    def conectar(self, event):
        self.send_presence()
        self.get_roster()

    def mensaje(self, msg):
        if msg['type'] in ('normal', 'chat'):
            print(f"Se recivió un mensaje de {msg['from']} -> {msg['body']}")

    
    def inicio_sesion(self, jid, password):
        self.boundjid = JID(jid)
        self.password = password

        logging.basicConfig(level=logging.DEBUG)

        if self.connect():
            self.process()

            print("Inicio de sesion correcto ... ")

        else:
            print("Hubo error en el inicio de sesion ... ")

    def registrar_usuario(self):

        jid = xmpp.protocol.JID(self.boundjid.bare)
        cl = xmpp.Client(jid.getDomain(), debug=[])
        cl.connect(server=(SERVER, 5222))
        cl.auth(jid.getNode(), self.password, resource=jid.getResource())

        registrar = xmpp.Iq(typ='set')
        registrar.setID('reg1')
        registrar.addChild('query', namespace='jabber:iq:register')
        registrar.getTag('query').addChild('username', payload=jid.getNode())
        registrar.getTag('query').addChild('password', payload=self.password)

        try:
            resultado = cl.SendAndWaitForResponse(registrar, timeout=10)
            if resultado and resultado.getType() == 'result':
                print(resultado.getValue())
                print("Usuario registrado correctamente ... ")

            elif resultado and resultado.getType() == 'error':
                print("Error al registrar el usuario ... ")
                self.disconnect()

        except Exception as e:
            print("Error al registrar el usuario:  ", e)
            self.disconnect()


        