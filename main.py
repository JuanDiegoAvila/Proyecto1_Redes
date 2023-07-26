from client import Client
import logging

SERVER = "alumchat.xyz"

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
        # cliente.inicio_sesion(, contraseña)

    elif opcion == "2":
        print("\n================ Registro ================\n")

        jid = input("Ingrese su nuevo JID de la forma (nombre+carnet-texto) -> ")
        contraseña = input("Ingrese su contraseña -> ")

        nuevo = Client(jid + "@" + SERVER, contraseña)
        nuevo.registrar_usuario()

        # Regresar al menu principal luego del registro
        menu_principal()

    elif opcion == "3":
        print("\n\n\n Gracias por utilizar el chat ...  \n\n")

if __name__ == "__main__":
    
    # cliente = Client()
    menu_principal()
