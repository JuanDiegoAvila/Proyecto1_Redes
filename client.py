from slixmpp import *
from slixmpp import exceptions
import xmpp
import logging
import sys
import asyncio
from aioconsole import ainput, aprint
import base64

SERVER = "alumchat.xyz"

logging.basicConfig(level=logging.DEBUG, filename='debug_log.txt') # se escribe un archivo con los logs del servidor 

# Extraido de: "https://stackoverflow.com/questions/63860576/asyncio-event-loop-is-closed-when-using-asyncio-run"
if sys.platform == 'win32' and sys.version_info >= (3, 8): 
     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Client(ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.username = jid.split('@')[0]
        self.password = password
        self.conected = False
        self.en_chat = False

        self.register_plugin('xep_0313')    # Message Archive Management
        self.register_plugin('xep_0004')    # Data Forms
        self.register_plugin('xep_0045')    # Multi-User Chat

        self.add_event_handler("session_start", self.start) # se ejecuta cuando se inicia la sesion
        self.add_event_handler("message", self.message) # se ejecuta cuando se recibe un mensaje
        self.add_event_handler("disconnected", self.desconectar) # se ejecuta cuando se desconecta del servidor
        self.add_event_handler("changed_status", self.cambio_estado) # se ejecuta cuando se cambia el estado de la cuenta de algun contacto
        self.add_event_handler("groupchat_invite", self.invitacion_grupo) # se ejecuta cuando se recibe una invitacion a un grupo
    
    # Se muestra la invitacion a un grupo
    # No solo avisa sino tambien se une al grupo automaticamente
    async def invitacion_grupo(self, presence):
        await aprint("\n==========================================================\n")
        await aprint(f"Has sido invitado al grupo {presence['from']}")
        await aprint("\n==========================================================\n")
        await self.plugin['xep_0045'].join_muc(presence['from'], self.username) # se une al grupo automaticamente
        await aprint(f"\nTe has unido al grupo {presence['from']} exitosamente.\n")

    # Cambio de estado de algun contacto
    async def cambio_estado(self, presence):
        if 'conference' not in str(presence['from']): # Si no es un chat grupal mostrar el cambio de estado
            await aprint("\n==========================================================\n")
            estado_encoded = ''

            if presence['type'] == 'unavailable': # Si el estado es no disponible
                await aprint(f"{presence['from']} ha cambiado a estado no disponible.")
            else:
                
                # Se hace el decode del estado segun el tipo de estado
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

    # Desconexion del servidor
    def desconectar(self, event):
        print("\n==========================================================\n")
        print("Has sido desconectado del servidor.")
        print("\n==========================================================\n")
        self.conected = False # se cambia el estado de la variable para pare el while del menu principal
    
    # Inicia la conexion con el servidor, inicia la sesion con la informacion del cliente
    async def start(self, event):
        try:
            self.send_presence() # se envia la presencia del cliente
            await aprint("\n==========================================================\n")
            await aprint("Inicio de sesion correcto ... ")
            await aprint("\n==========================================================\n")
            
            await self.get_roster() # se actualiza el roster
            self.conected = True # se cambia el estado de la variable para el while del menu principal

            asyncio.create_task(self.run_main_event_loop()) # se crea un hilo para el menu principal
            
        except exceptions.IqError as e:
            await aprint("\n==========================================================\n")
            await aprint("Error en el inicio de sesion: %s" % e.iq['error']['text'])
            await aprint("\n==========================================================\n")
        except exceptions.IqTimeout:
            await aprint("\n==========================================================\n")
            await aprint("Tiempo de inicio de sesion excedido.")
            await aprint("\n==========================================================\n")

    # Recibir un mensaje o un archivo tanto de un usuario como de un grupo
    async def message(self, msg):
    
        if msg['type'] in ('normal', 'chat'): # si es un mensaje normal o un chat, es decir con un solo usuario

            if 'file|' in msg['body']: # para recibir archivos
                partes = msg['body'].split('|') # se separa ya que estan separados por |
                extension = partes[1] 
                data = partes[2]
                data = base64.b64decode(data)
                with open(f"./archivos/recibido.{extension}", 'wb') as file: # se guarda el archivo en la carpeta archivos
                    file.write(data)
                    file.close()

                await aprint(f"\nSe recibio un archivo de {msg['from']} con extension {extension}.\n")

            if msg['from'] != self.jid: # asegura que no se imprima un mensaje enviado por el usuario
                if(self.en_chat): # si esta dentro de un chat personal
                    emisor = str(msg['from']).split('@')[0]
                    await aprint(f"\n{emisor} -> {msg['body']}")
                    await aprint('Mensaje -> ')
                else: # si esta en cualquier parte del programa menos en un chat personal
                    emisor = str(msg['from']).split('@')[0]
                    await aprint(f"\nSe recivió un mensaje de {emisor} -> {msg['body']}")

        if msg['type'] == 'groupchat': # si es un mensaje de un grupo
            de = str(msg['from']).split('/')[1] # se obtiene el nombre del usuario que envio el mensaje
            if de != self.username: # asegura que no se imprima un mensaje enviado por el usuario
                if(self.en_chat): # si esta dentro de un chat grupal
                    emisor = str(msg['from']).split('/')[1]
                    await aprint(f"\n{emisor} -> {msg['body']}")
                    await aprint('Mensaje -> ')
                else: # si esta en cualquier parte del programa menos en un chat grupal
                    group = str(msg['from']).split('/')[0]
                    emisor = str(msg['from']).split('/')[1]
                    await aprint(f"\nSe recivió un mensaje de {emisor} en el grupo {group} -> {msg['body']}")

    # Registro de un usuario en el servidor, se hace a traves de la libreria xmpp
    def registrar_usuario(self):
        jid = xmpp.JID(self.jid)
        account = xmpp.Client(jid.getDomain(), debug=[])
        account.connect()

        return bool( # se retorna un booleano para saber si se registro correctamente
            xmpp.features.register(account, jid.getDomain(),{
                'username': jid.getNode(),
                'password': self.password
            })
        )
    
    # Se desconecta del servidor
    async def cerrar_sesion(self):
        self.disconnect(wait=True)
        self.conected = False # se cambia el estado de la variable para pare el while del menu principal

    # Ver los contactos del cliente
    async def ver_contactos(self):
        await self.get_roster() # se actualiza el roster para tener los contactos actualizados
        roster = self.client_roster
        contacts = roster.keys()

        print("\n===================== Ver contactos ==========================\n")
        
        if not contacts: # si no hay contactos
            print("No tienes contactos.")
            return
        
        for contact in contacts:
            if contact != self.jid: # si el contacto no es el mismo usuario
                print(f"\n------------ {contact} ------------\n")
                presence = roster.presence(contact) # se obtiene la presencia del contacto

                for _, presence in presence.items():
                    if presence: # si el contacto esta conectado, se utiliza el show para saber el estado y el status para el mensaje
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


                if not presence: # si el contacto esta desconectado
                    print(f"\t\tEstado -> Desconectado")

            print(f"\n-------------{'-'*len(contact)}-------------\n")
                        
        input('\n\nPresiona ENTER para continuar ...\n\n')
        print("\n==========================================================\n")
            
    # Agregar un contacto
    async def agregar_contacto(self, jid):
        try:
            await aprint("\n===================== Agregar contacto ==========================\n")
            self.send_presence_subscription(pto=jid) # se envia la solicitud de contacto
            await self.get_roster() # se actualiza el roster para tener los contactos actualizados
            await aprint("\n==========================================================\n")
            await aprint("Solicitud de contacto enviada correctamente.")
            await aprint("\n==========================================================\n")
        except Exception as e:
            await aprint("\n==========================================================\n")
            await aprint(f"Error al agregar el contacto: {e}")
            await aprint("\n==========================================================\n")

    # Ver el detalle de un contacto en especifico
    async def ver_detalle_contacto(self, contacto):
        await self.get_roster() # se actualiza el roster para tener los contactos actualizados
        roster = self.client_roster
        contacts = roster.keys()
        
        if not contacts:
            print("No tienes contactos.")
            return
        
        cont_len = 0
        for contact in contacts:
            
            if contact != self.jid and contact == contacto: # si el contacto no es el mismo usuario y es el contacto que se busca
                print(f"\n------------ {contact} ------------\n")
                cont_len = len(contact)
                presence = roster.presence(contact) # se obtiene la presencia del contacto

                for _, presence in presence.items():
                    if presence: # si el contacto esta conectado, se utiliza el show para saber el estado y el status para el mensaje
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

                if not presence: # si el contacto esta desconectado
                    print(f"\t\tEstado -> Desconectado")
                        
        print(f"\n-------------{'-'*cont_len}-------------\n")

        
        input('Presiona ENTER para continuar ...\n\n')
        print("\n==========================================================\n")

    # Cambiar el estado de la cuenta
    async def cambiar_estado(self):
        print("\n===================== Cambiar estado/mensaje ==========================\n")
        await self.get_roster() # se actualiza el roster para tener los contactos actualizados
        print('\t[ 1 ] Estado.')
        print('\t[ 2 ] Mensaje. ')
        opcion = await ainput('\nOpcion -> ')

        if opcion == '1': # cambiar el estado
            print("\n==========================================================\n")
            print('\t[ 1 ] Disponible.')
            print('\t[ 2 ] Ocupado. ')
            print('\t[ 3 ] No disponible. ')
            print('\t[ 4 ] Ausente. ')
            opcion = input('\nOpcion -> ')
            
            # se envia la presencia con el estado seleccionado
            if opcion == '1':
                self.send_presence(pshow='chat')
            elif opcion == '2':
                self.send_presence(pshow='dnd')
            elif opcion == '3':
                self.send_presence(pshow='xa')
            elif opcion == '4':
                self.send_presence(pshow='away')
        
        elif opcion == '2': # cambiar el mensaje
            print("\n==========================================================\n")
            mensaje = input('Mensaje -> ')
            self.send_presence(pstatus=mensaje) # se envia la presencia con el mensaje seleccionado

        await ainput('\nPresiona ENTER para continuar ...\n\n')
        await aprint("\n==========================================================\n")

    # Eliminar la cuenta del servidor, se hace a traves de un stanza ya que la libreria no tiene un metodo para eliminar la cuenta
    def eliminar_cuenta(self):
        delete_stanza = f""" 
                <iq type="set" id="delete-account">
                <query xmlns="jabber:iq:register">
                    <remove jid="{self.username}"/>
                </query>
                </iq>
            """

        print(self.send_raw(delete_stanza))  # Se envia la stanza
        self.conected = False   # Para el while del menu principal

    # Se envia un mensaje a un usuario
    async def enviar_mensaje(self, destinatario):
        await aprint(f"\n===================== Chat con {destinatario} ==========================\n")
        
        mensaje = ''
        while mensaje != 'salir': # mientras no se escriba salir, para simular un chat continuo
            self.en_chat = True # se cambia el estado de la variable para que se imprima el mensaje en el chat
            await self.get_roster() # se actualiza el roster para tener la informacion actualizada
            mensaje = await ainput("Mensaje -> ") # se obtiene el mensaje
            
            if mensaje != 'salir':
                self.send_message(mto=destinatario, mbody=mensaje, mtype='chat') # se envia el mensaje

        self.en_chat = False # se cambia el estado de la variable para que se imprima el mensaje en el menu principal
        await aprint("\n==============================================================================\n")

    # Se elijen los contactos para agregarlos al grupo
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
                if contact != self.jid and contact not in contactos_agregados: # si el contacto no es el mismo usuario y no esta en el grupo
                    await aprint(f"\t[ {num} ] {contact} ")
                    act += 1 
                    con[num] = contact  # se guarda el contacto en un diccionario para saber a que contacto corresponde el numero
                    num += 1 

            if act != 0:
                opcion = await ainput("\nIngrese un contacto para agregar al grupo o escriba 'crear' para terminar -> ")
                if opcion != 'crear':
                    contactos_agregados.append(con[int(opcion)]) # se agrega el contacto a la lista de contactos del grupo
                
            else:
                opcion = 'crear'

        await aprint("\n==========================================================\n")
        return contactos_agregados 
    
    # Crear un grupo
    async def crear_grupo(self, nombre):
        
        contactos_agregados = await self.elejir_contactos() # obtener los contactos del usuario para agregar al grupo
        # crear el grupo
        room_jid = f"{nombre}@conference.{SERVER}"

        await self.plugin['xep_0045'].join_muc(room_jid, self.username) # unirse al grupo
        # await asyncio.sleep(1)
        response = self.plugin['xep_0004'].make_form(ftype='submit', title='Configuracion del grupo') # configurar el grupo

        # configuracion del grupo
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

        await self.plugin['xep_0045'].set_room_config(room_jid, config=response) # se configura el grupo

        # agregar los contactos al grupo
        for contacto in contactos_agregados: 
            self.plugin['xep_0045'].invite(room=room_jid, jid=contacto, reason=None) # se invita a los contactos seleccionados
        
        await ainput('\nSe creo el grupo exisosamente. Presiona ENTER para continuar ...\n\n')
        await aprint("\n==========================================================\n")

    # Unirse a un grupo existente
    async def unirse_a_grupo(self, nombre):
        room_jid = f"{nombre}@conference.{SERVER}" # se obtiene el jid del grupo
        try:
            await self.plugin['xep_0045'].join_muc(room_jid, self.username) # se une al grupo
            
            await ainput('\nSe unio al grupo exisosamente. Presiona ENTER para continuar ...\n\n')
        except Exception as e:
            await aprint("\n==========================================================\n")
            await aprint(f"Error al unirse al grupo: {e}")

        await aprint("\n==========================================================\n")

    # Invitar a un usuario a un grupo
    async def invitar_a_grupo(self, nombre):
        contactos_agregados = await self.elejir_contactos() # obtener los contactos del usuario para agregar al grupo
        room_jid = f"{nombre}@conference.{SERVER}" # se obtiene el jid del grupo

        for contacto in contactos_agregados:
            self.plugin['xep_0045'].invite(room=room_jid, jid=contacto, reason=None) # se invita a los contactos seleccionados
        
        await ainput('\nSe invito usuarios a grup exisosamente. Presiona ENTER para continuar ...\n\n')

        await aprint("\n==========================================================\n")

    # Enviar un mensaje a un grupo
    async def enviar_mensaje_grupo(self, nombre):
        room_jid = f"{nombre}@conference.{SERVER}" # se obtiene el jid del grupo 
        mensaje = ''
        while mensaje != 'salir': # mientras no se escriba salir, para simular un chat continuo
            self.en_chat = True # se cambia el estado de la variable para que se imprima el mensaje en el chat
            await self.get_roster() # se actualiza el roster para tener la informacion actualizada
            mensaje = await ainput("Mensaje -> ") 
            
            if mensaje != 'salir':
                self.send_message(mto=room_jid, mbody=mensaje, mtype='groupchat') # se envia el mensaje
        await aprint("\n==============================================================================\n")

    # Enviar un archivo a un usuario
    async def enviar_archivo(self, nombre, path):
        print(f"\n===================== Enviar archivo ==========================\n")
        with open(path, 'rb') as file: # se abre el archivo y se codifica en base64
            data = file.read()
            base64_data = base64.b64encode(data).decode('utf-8') 

        contenido = "file|" + path.split('.')[-1] + "|" + base64_data  # se concatena el tipo de archivo, la extension y el archivo codificado en base64

        self.send_message(mto=nombre, mbody=contenido, mtype="chat") # se envia el archivo
        print(f"\n Archivo enviado a {nombre} correctamente!")

        print(f"\n================================================================\n")

    # Menu principal
    async def run_main_event_loop(self):

        while self.conected: # mientras este conectado al servidor
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
                await aprint("\n===================== Envio de mensajes ==========================\n")
                
                opcion_chat = 0
                while opcion_chat != '1' and opcion_chat != '2':
                    await aprint('\t[ 1 ] Chat.')
                    await aprint('\t[ 2 ] Enviar archivo. ')
                    opcion_chat = await ainput("\nOpcion -> ")

                if opcion_chat == '1':
                    jid = await ainput("Ingrese el JID del contacto -> ")
                    jid = jid + "@" + SERVER
                    await self.enviar_mensaje(jid)

                elif opcion_chat == '2':
                    jid = await ainput("Ingrese el JID del contacto -> ")
                    jid = jid + "@" + SERVER
                    archivo = await ainput("Ingrese la ruta del archivo -> ")
                    await self.enviar_archivo(jid, archivo)
            
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


    


