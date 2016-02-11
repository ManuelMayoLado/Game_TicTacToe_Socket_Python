# -*- coding: utf-8 -*-

#SERVIDOR 3 EN RAIA

import socket
import json
import sys
from threading import *
import traceback

#VARIABLES DO XOGO

lista_xogo = [[0,0,0],[0,0,0],[0,0,0]]
lista_colores = [[0,0,0],[0,0,0],[0,0,0]]
turno = 1
ganador = False

#VARIABLES SERVIDOR

HOST = '0.0.0.0'
PORT = 5123

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))

ERROR = False
xogadores = {}

print(HOST,PORT)

def enraia(list,xogador):
	for linha in range(len(list)):
		if "".join(map(str, list[linha])) == str(xogador)*3:
			lista_colores[linha] = [1,1,1]
			return xogador
	for columna in range(len(list)):
		if "".join(map(str, [list[0][columna],list[1][columna],list[2][columna]])) == str(xogador)*3:
			lista_colores[0][columna],lista_colores[1][columna],lista_colores[2][columna] = 1,1,1
			return xogador
	if "".join(map(str, [list[0][0],list[1][1],list[2][2]])) == str(xogador)*3:
		lista_colores[0][0],lista_colores[1][1],lista_colores[2][2] = 1,1,1
		return xogador
	if "".join(map(str, [list[0][2],list[1][1],list[2][0]])) == str(xogador)*3:
		lista_colores[0][2],lista_colores[1][1],lista_colores[2][0] = 1,1,1
		return xogador
	return False

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
		global xogadores
		ON = True
		while ON:
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
					ganhador = enraia(lista_xogo,self.xog)
					msg = json.dumps([lista_xogo,turno,ganhador,lista_colores])
					for x in xogadores.itervalues():
						x['actualizacions'].sendall(msg)
			else:
				self.sock.close()
				try:
					del xogadores[self.xog]
				except:
					print "Error ao eliminar un xogador!"
					xogadores = {}
				ON = False
		print u"> xogador: "+str(self.xog)+" "+str(self.sock)+" Eliminado!"

def run_server():
	global ERROR
	global turno
	serversocket.listen(1)
	while True:
		if len(xogadores) >= 2:
			print("Xa hai 2 xogadores conectados ao servidor")
		else:
			print("Servidor escoitando...")
		try:
			sock, addr = serversocket.accept()
		except KeyboardInterrupt:
			serversocket.close()
			sys.exit()
		d_xog = json.loads(sock.recv(1024))
		if d_xog == 0:
			print "xogador novo!"
			n_xog = len(xogadores) + 1
			if n_xog == 3:
				sock.close()
				continue
			xogadores[n_xog] = {'xogadas': sock, 'actualizacions': None, 'id': n_xog}
			sock.send(json.dumps(n_xog))
		elif not d_xog == 0:
			print 'Connected by', addr
			xogadores[d_xog]['actualizacions'] = sock
			procesando(xogadores[d_xog]['xogadas'], d_xog)
			sock.send(json.dumps([lista_xogo,turno]))
			print "xogadores:"
			for x in xogadores.values():
				print "\t"+str(x["id"])+": "+str(x)
			if len(xogadores) == 2:
				for x in xogadores.values():
					print "Enviando inicio a "+str(x)
					x["actualizacions"].send(json.dumps("inicio"))
				print u"Empezando a partida!"
		else:
			print "Envio ao servidor erroneo"
	sys.exit()

run_server()


