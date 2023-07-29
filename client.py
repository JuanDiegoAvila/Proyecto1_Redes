from slixmpp import *
from slixmpp import exceptions
import xmpp
import logging
import sys
import asyncio

SERVER = "alumchat.xyz"

logging.basicConfig(level=logging.DEBUG, filename='debug_log.txt')

if sys.platform == 'win32' and sys.version_info >= (3, 8):
     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Client(ClientXMPP):

    def __init__(self, jid, password):
        super(Client, self).__init__(jid, password)

        self.username = jid.split('@')[0]
        self.password = password
        self.conected = False

        # GENERADO CON CHAT GPT
        self.plugins = [
            'xep_0030',  # Service Discovery
            'xep_0199',  # XMPP Ping
            'xep_0045',  # Multi-User Chat (MUC)
            'xep_0198',  # Stream Management
            'xep_0077',  # In-Band Registration
            'xep_0004',  # Data Forms
            'xep_0085',  # Chat State Notifications
            'xep_0184',  # Message Delivery Receipts
        ]

        self.add_event_handler("session_start", self.conectar)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.desconectar)


    def desconectar(self, event):
        print("\n==========================================================\n")
        print("Has sido desconectado del servidor.")
        print("\n==========================================================\n")
        self.conected = False
    
    # Funcion para verificar si un plugin existe extraida de CHAT GPT
    def start_plugins(self):
        for plugin in self.plugins:
            self.register_plugin(plugin)

    def conectar(self, event):
        try:
            self.send_presence()
            self.get_roster()
            print("\n==========================================================\n")
            print("Inicio de sesion correcto ... ")
            print("\n==========================================================\n")
            self.conected = True
            
        except exceptions.IqError as e:
            print("\n==========================================================\n")
            print("Error en el inicio de sesion: %s" % e.iq['error']['text'])
            print("\n==========================================================\n")
        except exceptions.IqTimeout:
            print("\n==========================================================\n")
            print("Tiempo de inicio de sesion excedido.")
            print("\n==========================================================\n")

    def message(self, msg):
        if msg['type'] in ('normal', 'chat'):
            print("\n==========================================================\n")
            print(f"Se recivió un mensaje de {msg['from']} -> {msg['body']}")
            print("\n==========================================================\n")

    def registrar_usuario(self):

        jid = xmpp.JID(self.jid)
        account = xmpp.Client(jid.getDomain(), debug=[])
        account.connect()

        return bool(
            xmpp.features.register(account, jid.getDomain(),{
                'username': jid.getNode(),
                'password': self.password
            })
        )
    
    def cerrar_sesion(self):
        self.disconnect(wait=True)

    def enviar_mensaje(self, destinatario, mensaje):
        self.send_message(mto=destinatario, mbody=mensaje, mtype='chat')
    
    def enviar_mensaje_grupo(self, destinatario, mensaje):
        self.send_message(mto=destinatario, mbody=mensaje, mtype='groupchat')

    def crear_grupo(self, nombre_grupo):
        self.plugin['xep_0045'].join_muc(nombre_grupo, self.username)

    def cambiar_estado(self, estado):
        self.send_presence(pshow=estado)

    def eliminar_cuenta(self):
        self.plugin['xep_0030'].del_item(node='account')
