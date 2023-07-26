from slixmpp import *
import logging

logging.basicConfig(level=logging.DEBUG, filename='debug_log.txt')

class Client(ClientXMPP):

    def __init__(self, jid, password):
        super(Client, self).__init__(jid, password)

        self.add_event_handler("session_start", self.conectar)
        self.add_event_handler("message", self.mensaje)

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

        else:
            print("Hubo error en el inicio de sesion ... ")

    def registrar_usuario(self):
        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0004")  # Data forms
        self.register_plugin("xep_0066")  # Out-of-band Data
        self.register_plugin("xep_0077")  # In-band Registration

        logging.basicConfig(level=logging.DEBUG)

        if self.connect():
            self.process(register=True)

        else:
            print("No se pudo registrar al usuario ...")