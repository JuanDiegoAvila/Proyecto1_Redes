# Proyecto1_Redes

## Characteristics
This proyect emulates a chat, and works with xmpp connection with the server alumchat.xyz. 
It allows the user, via CLI, to do the following:
- Login to the server.
- Register a new user.
- View contacts.
- Add contacts.
- View the details of a contact.
- Send a private message to a user.
- Send a file through private messages.
- Send a group message.
- Join a groupchat.
- Create a groupchat.
- Send a invite to a user to a groupchat.
- Change the users status or message.
- Delete the account from the server.
- Log out from server.

Many of the functionalities where made using the library `slixmpp`. Register was developed using the `xmpp` and the eliminar_cuenta function which deletes the account whas made with stanzas sent as raw content for easier implementation.
\
Many ideas for the implementation of this chat where extracted from:
- [Chat GPT](https://chat.openai.com)
- [Github Copilot](https://github.com/features/copilot)
- [Slixmpp Documentation](https://slixmpp.readthedocs.io/en/latest/)

\
A message scheme was established with classmates to receive and send messages in the following format: `file|EXTENSION|ENCODED DATA`


## Libraries
This proyect is developed in python `3.10.7` using the following libraries:
- `slixmpp` - `1.8.4` most of the functionalities where developed using this library which allows to create the xmpp client and to interact with the different functions available in this chat.
- `xmpp` or `xmpppy` - `0.7.1` was used in the register option. 
- `logging` was used to capture all the debug messages in the debug_log.txt to analize errors and messages from and to the server. Part of the python standard library.
- `sys` used in the configuration of the windows loop policy. Part of the python standard library.
- `asyncio` allowed to create threads and manage part of the asynchronous functions. Part of the python standard library.
- `aiconsole` - `0.6.2` to make the prints and inputs asynchronous to allow messages to be received and that the flow of the chat whas appropriate.
- `base64` to encode the content of the files and decode to be sent and received. Part of the python standard library.


## Instalation
To install and use this proyect just download all the libraries listed above with the versions where indicated. 
Clone the repository using the command: 
```bash
  git clone https://github.com/JuanDiegoAvila/Proyecto1_Redes.git
```
When you have the repository, in the root of the proyect use the command:
```bash
  python main.py
```
This will let you interact with all of the functionalities of the proyect.
If you want to send files make sure they are in the folder `./archivos`. In this folder you can find also the ones you recieve with the name `recibido.txt`.
\
If you also want to know what is happenind in the communication with the server you can view the file `debug_log.txt`.
