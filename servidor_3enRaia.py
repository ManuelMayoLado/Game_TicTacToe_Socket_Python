# -*- coding: utf-8 -*-

#SERVIDOR 3 EN RAIA

import socket
import json
import sys
from threading import *
import traceback

#VARIABLES DO XOGO

lista_xogo = [[0,0,0],[0,0,0],[0,0,0]]
turno = 1
ganador = False

#VARIABLES SERVIDOR

HOST = '0.0.0.0'
PORT = 50017

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))

ERROR = False

print(HOST,PORT)

class procesando(Thread):

    def __init__(self, socket, xog):
        Thread.__init__(self)
        self.sock = socket
        self.xog = xog
        self.start()

    def run(self):
        try:
                self.run_()
        except:
                traceback.print_exc()

    def run_(self):
        global lista_xogo
        global turno
        global ERROR
        ON = True
        while ON:
            print "volta de bucle"
            data = self.sock.recv(1024)
            if data:
                if data == "end":
                    ON = False
                    ERROR = True
                    break
                else:
                    print('Datos recividos:', data)
                    pos_cadro = json.loads(data)
                    lista_xogo[pos_cadro[1]][pos_cadro[0]] = self.xog
                    turno = 2 if self.xog == 1 else 1
                    msg = json.dumps([lista_xogo,turno])
                    for x in xogadores.itervalues():
                            x['actualizacions'].sendall(msg)
            else:
                sys.exit()
        print "...Servidor Desactivado"


xogadores = {}

def run():
    global ERROR
    global turno
    serversocket.listen(1)
    while True:
            print("Servidor escoitando...")
            try:
                sock, addr = serversocket.accept()
            except KeyboardInterrupt:
                serversocket.close()
                sys.exit()
            xog = json.loads(sock.recv(1024))
            print "Conectado!"
            if xog == "npi":
                    print "xogador novo!", xogadores
                    xog = len(xogadores) + 1
                    if xog == 3:
                            sock.close()
                            continue
                    xogadores[xog] = {'xogadas': sock, 'actualizacions': None, 'id': xog}
                    sock.send(json.dumps(xog))
            else:
                    print 'Connected by', addr
                    xogadores[xog]['actualizacions'] = sock
                    procesando(xogadores[xog]['xogadas'], xog)
    sys.exit()

run()


