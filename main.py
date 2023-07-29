from client import Client

SERVER = "alumchat.xyz"

def menu_chat(cliente):
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
        pass
    elif opcion == "2":
        pass
    elif opcion == "3":
        pass
    elif opcion == "4":
        pass
    elif opcion == "5":
        pass
    elif opcion == "6":
        pass
    elif opcion == "7":
        pass
    elif opcion == "8":
        cliente.eliminar_cuenta()
    elif opcion == "9":
        cliente.cerrar_sesion()
        menu_principal()

# Punto de entrada donde se maneja el menu del chat
def menu_principal():
    print("\n\n================ Bienvenido al chat - Proyecto 1 de Redes ================\n")
    print("[ 1 ] Iniciar sesion")
    print("[ 2 ] Registrarse")
    print("[ 3 ] Salir")
    opcion = input("\nIngrese una opcion -> ")
    
    if opcion == "1":
        print("\n================ Inicio de sesion ================\n")

        jid = input("Ingrese su JID de la forma (nombre+carnet-texto) -> ")
        contraseña = input("Ingrese su contraseña -> ")

        cliente = Client(jid + "@" + SERVER, contraseña)
        
        cliente.start_plugins()
        cliente.connect(disable_starttls=True, use_ssl=False)
        cliente.process(forever=False)

        if cliente.connected:
            # mandar a menu de chat
            menu_chat(cliente)
        
        
    elif opcion == "2":
        print("\n================ Registro ================\n")

        jid = input("Ingrese su nuevo JID de la forma (nombre+carnet-texto) -> ")
        contraseña = input("Ingrese su contraseña -> ")

        nuevo_usuario = Client(jid + "@" + SERVER, contraseña)
        nuevo_usuario.registrar_usuario()
        nuevo_usuario.disconnect()

        # Regresar al menu principal luego del registro
        menu_principal()

    elif opcion == "3":
        print("\n\n\n Gracias por utilizar el chat ...  \n\n")

if __name__ == "__main__":
    menu_principal()