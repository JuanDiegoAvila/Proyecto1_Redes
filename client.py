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
        super().__init__(jid, password)

        self.username = jid.split('@')[0]
        self.password = password
        self.conected = False

        self.register_plugin('xep_0313') 

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.desconectar)

    def desconectar(self, event):
        print("\n==========================================================\n")
        print("Has sido desconectado del servidor.")
        print("\n==========================================================\n")
        self.conected = False
    
    async def start(self, event):
        try:
            self.send_presence()
            print("\n==========================================================\n")
            print("Inicio de sesion correcto ... ")
            print("\n==========================================================\n")
            
            await self.get_roster()
            self.conected = True

            asyncio.create_task(self.run_main_event_loop())
            
        except exceptions.IqError as e:
            print("\n==========================================================\n")
            print("Error en el inicio de sesion: %s" % e.iq['error']['text'])
            print("\n==========================================================\n")
        except exceptions.IqTimeout:
            print("\n==========================================================\n")
            print("Tiempo de inicio de sesion excedido.")
            print("\n==========================================================\n")

    async def message(self, msg):
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
    
    async def cerrar_sesion(self):
        self.disconnect(wait=True)
        self.conected = False

    async def ver_contactos(self):
        await self.get_roster()
        roster = self.client_roster
        contacts = roster.keys()

        print("\n===================== Ver contactos ==========================\n")
        
        if not contacts:
            print("No tienes contactos.")
            return
        
        
        for contact in contacts:
            
            if contact != self.jid:
                print(f"\n------------ {contact} ------------\n")
                presence = roster.presence(contact)

                for _, presence in presence.items():
                    if presence:
                        tiene = False
                        if presence['show']:
                            tiene = True
                            if presence['show'] == 'dnd':
                                print(f"\t\tEstado -> Ocupado")

                            elif presence['show'] == 'xa':
                                print(f"\t\tEstado -> No disponible")

                            elif presence['show'] == 'away':
                                print(f"\t\tEstado -> Ausente")
                        
                        else:
                            if not tiene:
                                print(f"\t\tEstado -> Disponible")
                            
                        if presence['status']:
                            print(f'\t\tMensaje -> {presence["status"]}')


                if not presence:
                    print(f"\t\tEstado -> Desconectado")

            print(f"\n-------------{'-'*len(contact)}-------------\n")
                        


        
        input('\n\nPresiona ENTER para continuar ...\n\n')
        
        print("\n==========================================================\n")
            
    
      
    async def agregar_contacto(self, jid):
        try:
            print("\n===================== Agregar contacto ==========================\n")
            self.send_presence_subscription(pto=jid)
            await self.get_roster()
            print("\n==========================================================\n")
            print("Solicitud de contacto enviada correctamente.")
            print("\n==========================================================\n")
        except Exception as e:
            print("\n==========================================================\n")
            print(f"Error al agregar el contacto: {e}")
            print("\n==========================================================\n")

    async def ver_detalle_contacto(self, contacto):
        await self.get_roster()
        roster = self.client_roster
        contacts = roster.keys()
        
        if not contacts:
            print("No tienes contactos.")
            return
        
        cont_len = 0
        for contact in contacts:
            
            if contact != self.jid and contact == contacto:
                print(f"\n------------ {contact} ------------\n")
                cont_len = len(contact)
                presence = roster.presence(contact)

                for _, presence in presence.items():
                    if presence:
                        tiene = False
                        if presence['show']:
                            tiene = True
                            if presence['show'] == 'dnd':
                                print(f"\t\tEstado -> Ocupado")

                            elif presence['show'] == 'xa':
                                print(f"\t\tEstado -> No disponible")

                            elif presence['show'] == 'away':
                                print(f"\t\tEstado -> Ausente")
                        
                        else:
                            if not tiene:
                                print(f"\t\tEstado -> Disponible")
                            
                        if presence['status']:
                            print(f'\t\tMensaje -> {presence["status"]}')

                if not presence:
                    print(f"\t\tEstado -> Desconectado")
                        
        print(f"\n-------------{'-'*cont_len}-------------\n")

        
        input('Presiona ENTER para continuar ...\n\n')
        print("\n==========================================================\n")


    async def cambiar_estado(self):
        print("\n===================== Cambiar estado/mensaje ==========================\n")
        await self.get_roster()
        print('\t[ 1 ] Estado.')
        print('\t[ 2 ] Mensaje. ')
        opcion = input('\nOpcion -> ')

        if opcion == '1':
            print("\n==========================================================\n")
            print('\t[ 1 ] Disponible.')
            print('\t[ 2 ] Ocupado. ')
            print('\t[ 3 ] No disponible. ')
            print('\t[ 4 ] Ausente. ')
            opcion = input('\nOpcion -> ')
            
            if opcion == '1':
                self.send_presence(pshow='chat')
            elif opcion == '2':
                self.send_presence(pshow='dnd')
            elif opcion == '3':
                self.send_presence(pshow='xa')
            elif opcion == '4':
                self.send_presence(pshow='away')
        
        elif opcion == '2':
            print("\n==========================================================\n")
            mensaje = input('Mensaje -> ')
            self.send_presence(pstatus=mensaje)

        input('\nPresiona ENTER para continuar ...\n\n')
        print("\n==========================================================\n")

    def eliminar_cuenta(self):
        delete_stanza = f"""
                <iq type="set" id="delete-account">
                <query xmlns="jabber:iq:register">
                    <remove jid="{self.username}"/>
                </query>
                </iq>
            """

        print(self.send_raw(delete_stanza))
        self.conected = False

    async def enviar_mensaje(self, destinatario):
        print(f"\n===================== Chat con {destinatario} ==========================\n")
        
        mensaje = ''
        while mensaje != 'salir':
            await self.get_roster()
            mensaje = input("Mensaje -> ")
            
            if mensaje != 'salir':
                self.send_message(mto=destinatario, mbody=mensaje, mtype='chat')
        print("\n==============================================================================\n")

    async def run_main_event_loop(self):

        while self.conected:
            print("\n\n================ Menu de chat ================\n")
            print("[ 1 ] Ver contactos")
            print("[ 2 ] Agregar contactos")
            print("[ 3 ] Ver detalle de contacto")
            print("[ 4 ] Enviar mensaje a un usuario")
            print("[ 5 ] Enviar mensaje a un grupo")
            print("[ 6 ] Crear grupo")
            print("[ 7 ] Cambiar estado de cuenta")
            print("[ 8 ] Eliminar cuenta del servidor")
            print("[ 9 ] Cerrar sesion")
            opcion = input("\nIngrese una opcion -> ")

            if opcion == "1":
                await self.ver_contactos()

            elif opcion == "2":
                jid = input("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.agregar_contacto(jid)

            elif opcion == "3":
                
                print("\n===================== Ver detalle de contacto ==========================\n")
                jid = input("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.ver_detalle_contacto(jid)

            elif opcion == "4":
                print("\n===================== Enviar mensaje a un usuario ==========================\n")
                jid = input("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.enviar_mensaje(jid)
            elif opcion == "5":
                pass
            elif opcion == "6":
                pass
            elif opcion == "7":
                await self.cambiar_estado()
            elif opcion == "8":
                self.eliminar_cuenta()
            elif opcion == "9":
                await self.cerrar_sesion()

    # def enviar_mensaje_grupo(self, destinatario, mensaje):
    #     self.send_message(mto=destinatario, mbody=mensaje, mtype='groupchat')

    # def crear_grupo(self, nombre_grupo):
    #     self.plugin['xep_0045'].join_muc(nombre_grupo, self.username)

    


