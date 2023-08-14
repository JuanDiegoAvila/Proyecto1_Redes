from slixmpp import *
from slixmpp import exceptions
import xmpp
import logging
import sys
import asyncio
from aioconsole import ainput, aprint
import base64

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
        self.add_event_handler("groupchat_invite", self.invitacion_grupo)
    
    async def invitacion_grupo(self, presence):
        await aprint("\n==========================================================\n")
        await aprint(f"Has sido invitado al grupo {presence['from']}")
        await aprint("\n==========================================================\n")
        await self.plugin['xep_0045'].join_muc(presence['from'], self.username)
        await aprint(f"\nTe has unido al grupo {presence['from']} exitosamente.\n")

    async def cambio_estado(self, presence):
        if 'conference' not in str(presence['from']):
            await aprint("\n==========================================================\n")
            estado_encoded = ''

            if presence['type'] == 'unavailable':
                await aprint(f"{presence['from']} ha cambiado a estado no disponible.")
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
                    
                await aprint(f"{presence['from']} ha cambiado a estado {estado_encoded}: {status}")
            await aprint("\n==========================================================\n")

    def desconectar(self, event):
        print("\n==========================================================\n")
        print("Has sido desconectado del servidor.")
        print("\n==========================================================\n")
        self.conected = False
    
    async def start(self, event):
        try:
            self.send_presence()
            await aprint("\n==========================================================\n")
            await aprint("Inicio de sesion correcto ... ")
            await aprint("\n==========================================================\n")
            
            await self.get_roster()
            self.conected = True

            asyncio.create_task(self.run_main_event_loop())
            
        except exceptions.IqError as e:
            await aprint("\n==========================================================\n")
            await aprint("Error en el inicio de sesion: %s" % e.iq['error']['text'])
            await aprint("\n==========================================================\n")
        except exceptions.IqTimeout:
            await aprint("\n==========================================================\n")
            await aprint("Tiempo de inicio de sesion excedido.")
            await aprint("\n==========================================================\n")

    async def message(self, msg):
    
        if msg['type'] in ('normal', 'chat'):
            if msg['from'] != self.jid:
                if(self.en_chat):
                    emisor = str(msg['from']).split('@')[0]
                    await aprint(f"\n{emisor} -> {msg['body']}")
                    await aprint('Mensaje -> ')
                else:
                    emisor = str(msg['from']).split('@')[0]
                    await aprint(f"\nSe recivió un mensaje de {emisor} -> {msg['body']}")

        if msg['type'] == 'groupchat':
            de = str(msg['from']).split('/')[1]
            if de != self.username:
                if(self.en_chat):
                    emisor = str(msg['from']).split('/')[1]
                    await aprint(f"\n{emisor} -> {msg['body']}")
                    await aprint('Mensaje -> ')
                else:
                    group = str(msg['from']).split('/')[0]
                    emisor = str(msg['from']).split('/')[1]
                    await aprint(f"\nSe recivió un mensaje de {emisor} en el grupo {group} -> {msg['body']}")

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
            await aprint("\n===================== Agregar contacto ==========================\n")
            self.send_presence_subscription(pto=jid)
            await self.get_roster()
            await aprint("\n==========================================================\n")
            await aprint("Solicitud de contacto enviada correctamente.")
            await aprint("\n==========================================================\n")
        except Exception as e:
            await aprint("\n==========================================================\n")
            await aprint(f"Error al agregar el contacto: {e}")
            await aprint("\n==========================================================\n")

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
        await aprint("\n===================== Cambiar estado/mensaje ==========================\n")
        await self.get_roster()
        await aprint('\t[ 1 ] Estado.')
        await aprint('\t[ 2 ] Mensaje. ')
        opcion = await ainput('\nOpcion -> ')

        if opcion == '1':
            await aprint("\n==========================================================\n")
            await aprint('\t[ 1 ] Disponible.')
            await aprint('\t[ 2 ] Ocupado. ')
            await aprint('\t[ 3 ] No disponible. ')
            await aprint('\t[ 4 ] Ausente. ')
            opcion = await ainput('\nOpcion -> ')
            
            if opcion == '1':
                self.send_presence(pshow='chat')
            elif opcion == '2':
                self.send_presence(pshow='dnd')
            elif opcion == '3':
                self.send_presence(pshow='xa')
            elif opcion == '4':
                self.send_presence(pshow='away')
        
        elif opcion == '2':
            await aprint("\n==========================================================\n")
            mensaje = await ainput('Mensaje -> ')
            self.send_presence(pstatus=mensaje)

        await ainput('\nPresiona ENTER para continuar ...\n\n')
        await aprint("\n==========================================================\n")

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
        await aprint(f"\n===================== Chat con {destinatario} ==========================\n")
        
        mensaje = ''
        while mensaje != 'salir':
            self.en_chat = True
            await self.get_roster()
            mensaje = await ainput("Mensaje -> ")
            
            if mensaje != 'salir':
                self.send_message(mto=destinatario, mbody=mensaje, mtype='chat')
        await aprint("\n==============================================================================\n")

    async def elejir_contactos(self):
        # obtener los contactos del usuario y mostrarlos para que elija
        await self.get_roster()
        contactos_agregados = []
        contacts = self.client_roster.keys()

        if not contacts:
            await aprint("No tienes contactos.")
            return

        await aprint("\n===================== Contactos ==========================\n")
        opcion = 0
        while opcion != 'crear':
            
            num = 1
            con = {}
            act = 0

            for contact in contacts:
                if contact != self.jid and contact not in contactos_agregados:
                    await aprint(f"\t[ {num} ] {contact} ")
                    act += 1
                    con[num] = contact
                    num += 1

            if act != 0:
                opcion = await ainput("\nIngrese un contacto para agregar al grupo o escriba 'crear' para terminar -> ")
                if opcion != 'crear':
                    contactos_agregados.append(con[int(opcion)])
                
            else:
                opcion = 'crear'
        await aprint(contactos_agregados)
        await aprint("\n==========================================================\n")
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
        
        await ainput('\nSe creo el grupo exisosamente. Presiona ENTER para continuar ...\n\n')
        await aprint("\n==========================================================\n")

    async def unirse_a_grupo(self, nombre):
        room_jid = f"{nombre}@conference.{SERVER}"
        try:
            await self.plugin['xep_0045'].join_muc(room_jid, self.username)
            
            await ainput('\nSe unio al grupo exisosamente. Presiona ENTER para continuar ...\n\n')
        except Exception as e:
            await aprint("\n==========================================================\n")
            await aprint(f"Error al unirse al grupo: {e}")

        await aprint("\n==========================================================\n")

    async def invitar_a_grupo(self, nombre):
        contactos_agregados = await self.elejir_contactos()
        room_jid = f"{nombre}@conference.{SERVER}"

        for contacto in contactos_agregados:
            self.plugin['xep_0045'].invite(room=room_jid, jid=contacto, reason=None)
        
        await ainput('\nSe invito usuarios a grup exisosamente. Presiona ENTER para continuar ...\n\n')

        await aprint("\n==========================================================\n")

    async def enviar_mensaje_grupo(self, nombre):
        room_jid = f"{nombre}@conference.{SERVER}"
        mensaje = ''
        while mensaje != 'salir':
            self.en_chat = True
            await self.get_roster()
            mensaje = await ainput("Mensaje -> ")
            
            if mensaje != 'salir':
                self.send_message(mto=room_jid, mbody=mensaje, mtype='groupchat')
        await aprint("\n==============================================================================\n")

    async def enviar_archivo(self, nombre, path):
        with open(path, 'rb') as file:
            data = file.read()
            file_data_base64 = base64.b64encode(data).decode('utf-8')

        message = "file|" + path.split('.')[-1] + "|" + file_data_base64 

        self.send_message(mto=nombre, mbody=message, mtype='chat')
        print(f"File '{path}' enviado a {path}")

    async def run_main_event_loop(self):

        while self.conected:
            await aprint("\n\n================ Menu de chat ================\n")
            await aprint("[ 1 ] Ver contactos")
            await aprint("[ 2 ] Agregar contactos")
            await aprint("[ 3 ] Ver detalle de contacto")
            await aprint("[ 4 ] Enviar mensaje a un usuario")
            await aprint("[ 5 ] Enviar mensaje a un grupo")
            await aprint("[ 6 ] Crear grupo")
            await aprint("[ 7 ] Unirse a un grupo")
            await aprint("[ 8 ] Invitar a un usuario a un grupo")
            await aprint("[ 9 ] Cambiar estado de cuenta")
            await aprint("[ 10 ] Eliminar cuenta del servidor")
            await aprint("[ 11 ] Cerrar sesion")
            opcion = await ainput("\nIngrese una opcion -> ")

            if opcion == "1":
                await self.ver_contactos()

            elif opcion == "2":
                await aprint("\n===================== Agregar contacto ==========================\n")
                jid = await ainput("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.agregar_contacto(jid)

            elif opcion == "3":
                
                await aprint("\n===================== Ver detalle de contacto ==========================\n")
                jid = await ainput("Ingrese el JID del contacto -> ")
                jid = jid + "@" + SERVER
                await self.ver_detalle_contacto(jid)

            elif opcion == "4":
                await aprint("\n===================== Enviar mensaje a un usuario ==========================\n")
                
                opcion_chat = 0
                while opcion_chat != '1' and opcion_chat != '2':
                    await aprint('\t[ 1 ] Chat.')
                    await aprint('\t[ 2 ] Enviar archivo. ')
                    opcion_chat = await ainput("\nOpcion -> ")

                if opcion_chat == '1':
                    jid = await ainput("Ingrese el JID del contacto -> ")
                    jid = jid + "@" + SERVER
                    await self.enviar_mensaje(jid)

                # elif opcion_chat == '2':
                #     jid = await ainput("Ingrese el JID del contacto -> ")
                #     jid = jid + "@" + SERVER
                #     archivo = await ainput("Ingrese la ruta del archivo -> ")
                #     await self.send_file(jid, archivo)
            
            elif opcion == "5":
                await aprint("\n===================== Enviar mensaje a un grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.enviar_mensaje_grupo(nombre_grupo)
            
            elif opcion == "6":
                await aprint("\n===================== Crear grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.crear_grupo(nombre_grupo)
            
            elif opcion == "7":
                await aprint("\n===================== Unirse a grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.unirse_a_grupo(nombre_grupo)
            
            elif opcion == "8":
                await aprint("\n===================== Invitar a grupo ==========================\n")
                nombre_grupo = await ainput("Ingrese el nombre del grupo -> ")
                await self.invitar_a_grupo(nombre_grupo)
            
            elif opcion == "9":
                await self.cambiar_estado()
            
            elif opcion == "10":
                self.eliminar_cuenta()
            
            elif opcion == "11":
                await self.cerrar_sesion()


    


