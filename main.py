from client import Client
import asyncio

SERVER = "alumchat.xyz"
            
# Punto de entrada donde se maneja el menu del chat
def menu_principal():
    opcion = 0
    while opcion != '3':
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
            
            # cliente.start_plugins()
            cliente.connect(disable_starttls=True, use_ssl=False)
            cliente.process(forever=False)
            
            
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