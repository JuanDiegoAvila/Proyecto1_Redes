from slixmpp import *
from slixmpp import exceptions
import xmpp
import logging
import sys
import asyncio
from aioconsole import ainput

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
        self.en_chat = False

        self.register_plugin('xep_0313') 
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0045')

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.desconectar)
        # self.add_event_handler("subscribed", self.solicitud_contacto)
        self.add_event_handler("changed_status", self.cambio_estado)

    async def cambio_estado(self, presence):
        print("\n==========================================================\n")
        estado_encoded = ''

        if presence['type'] == 'unavailable':
            print(f"{presence['from']} ha cambiado a estado no disponible.")
        else:
            estado = presence['show']
            status = presence['status']
            if estado == 'dnd':
                estado_encoded = 'Ocupado'
            elif estado == 'xa':
                estado_encoded = 'No disponible'
            elif estado == 'away':
                estado_encoded = 'Ausente'
            else:
                estado_encoded = 'Disponible'
                
            print(f"{presence['from']} ha cambiado a estado {estado_encoded}: {status}")
        print("\n==========================================================\n")

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
            if(self.en_chat):
                emisor = msg['from'].split('@')[0]
                print(f"{emisor} -> {msg['body']}")
            
            else:
                emisor = msg['from'].split('@')[0]
                print(f"Se recivió un mensaje de {emisor} -> {msg['body']}")

        if msg['type'] == 'groupchat':
            if(self.en_chat):
                emisor = msg['from'].split('/')[1]
                print(f"{emisor} -> {msg['body']}")
            else:
                group = msg['from'].split('/')[0]
                emisor = msg['from'].split('/')[1]
                print(f"Se recivió un mensaje de {emisor} en el grupo {group} -> {msg['body']}")

    # async def solicitud_contacto(self, presence):
    #     print("\n==========================================================\n")
    #     if presence["type"] == "subscribe":
    #         print(f"Recibida solicitud de contacto de: {presence['from']}")
    #         self.send_presence(pto=presence['from'], ptype='subscribed')
    #     print("\n==========================================================\n")

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
            self.en_chat = True
            await self.get_roster()
            mensaje = input("Mensaje -> ")
            
            if mensaje != 'salir':
                self.send_message(mto=destinatario, mbody=mensaje, mtype='chat')
        print("\n==============================================================================\n")

    async def elejir_contactos(self):
        # obtener los contactos del usuario y mostrarlos para que elija
        await self.get_roster()
        contactos_agregados = []
        contacts = self.client_roster.keys()

        if not contacts:
            print("No tienes contactos.")
            return

        print("\n===================== Contactos ==========================\n")
        opcion = 0
        while opcion != 'crear':
            
            num = 1
            con = {}
            act = 0

            for contact in contacts:
                if contact != self.jid and contact not in contactos_agregados:
                    print(f"\t[ {num} ] {contact} ")
                    act += 1
                    con[num] = contact
                    num += 1

            if act != 0:
                opcion = input("\nIngrese un contacto para agregar al grupo o escriba 'crear' para terminar -> ")
                if opcion != 'crear':
                    contactos_agregados.append(con[int(opcion)])
                
            else:
                opcion = 'crear'

        print("\n==========================================================\n")
        return contactos_agregados
    
    async def crear_grupo(self, nombre):
        
        contactos_agregados = await self.elejir_contactos()
        # crear el grupo
        room_jid = f"{nombre}@conference.{SERVER}"

        await self.plugin['xep_0045'].join_muc(room_jid, self.username)
        # await asyncio.sleep(1)
        response = self.plugin['xep_0004'].make_form(ftype='submit', title='Configuracion del grupo')

        response['muc#roomconfig_roomname'] = nombre
        response['muc#roomconfig_persistentroom'] = '1'
        response['muc#roomconfig_publicroom'] = '1'
        response['muc#roomconfig_membersonly'] = '0'
        response['muc#roomconfig_allowinvites'] = '1'
        response['muc#roomconfig_enablelogging'] = '1'
        response['muc#roomconfig_changesubject'] = '1'
        response['muc#roomconfig_maxusers'] = '100'
        response['muc#roomconfig_whois'] = 'anyone'
        response['muc#roomconfig_roomdesc'] = 'Chat con mis contactos'
        response['muc#roomconfig_roomowners'] = self.username

        await self.plugin['xep_0045'].set_room_config(room_jid, config=response)

        # agregar los contactos al grupo
        for contacto in contactos_agregados:
            self.plugin['xep_0045'].invite(room=room_jid, jid=contacto, reason=None)
        
        input('\nSe creo el grupo exisosamente. Presiona ENTER para continuar ...\n\n')
        print("\n==========================================================\n")

    async def unirse_a_grupo(self, nombre):
        room_jid = f"{nombre}@conference.{SERVER}"
        await self.plugin['xep_0045'].join_muc(room_jid, self.username)
        
        input('\nSe unio al grupo exisosamente. Presiona ENTER para continuar ...\n\n')

        print("\n==========================================================\n")

    async def invitar_a_grupo(self, nombre):
        contactos_agregados = await self.elejir_contactos()
        room_jid = f"{nombre}@conference.{SERVER}"

        for contacto in contactos_agregados:
            self.plugin['xep_0045'].invite(room=room_jid, jid=contacto, reason=None)
        
        input('\nSe invito usuarios a grup exisosamente. Presiona ENTER para continuar ...\n\n')

        print("\n==========================================================\n")

    async def enviar_mensaje_grupo(self, nombre):
        room_jid = f"{nombre}@conference.{SERVER}"
        mensaje = ''
        while mensaje != 'salir':
            self.en_chat = True
            await self.get_roster()
            mensaje = input("Mensaje -> ")
            
            if mensaje != 'salir':
                self.send_message(mto=room_jid, mbody=mensaje, mtype='groupchat')
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
            print("[ 7 ] Unirse a un grupo")
            print("[ 8 ] Invitar a un usuario a un grupo")
            print("[ 9 ] Cambiar estado de cuenta")
            print("[ 10 ] Eliminar cuenta del servidor")
            print("[ 11 ] Cerrar sesion")
            opcion = await ainput("\nIngrese una opcion -> ")

            if opcion == "1":
                await self.ver_contactos()

            elif opcion == "2":
                print("\n===================== Agregar contacto ==========================\n")
                jid = await ainput("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.agregar_contacto(jid)

            elif opcion == "3":
                
                print("\n===================== Ver detalle de contacto ==========================\n")
                jid = await ainput("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.ver_detalle_contacto(jid)

            elif opcion == "4":
                print("\n===================== Enviar mensaje a un usuario ==========================\n")
                jid = await ainput("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.enviar_mensaje(jid)
            
            elif opcion == "5":
                print("\n===================== Enviar mensaje a un grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.enviar_mensaje_grupo(nombre_grupo)
            
            elif opcion == "6":
                print("\n===================== Crear grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.crear_grupo(nombre_grupo)
            
            elif opcion == "7":
                print("\n===================== Unirse a grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.unirse_a_grupo(nombre_grupo)
            
            elif opcion == "8":
                print("\n===================== Invitar a grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.invitar_a_grupo(nombre_grupo)
            
            elif opcion == "9":
                await self.cambiar_estado()
            
            elif opcion == "10":
                self.eliminar_cuenta()
            
            elif opcion == "11":
                await self.cerrar_sesion()


    


