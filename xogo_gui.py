# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import socket
import json
import sys

#SERVIDOR E PUERTO
HOST = raw_input(u">>> Server: ")
PORT = 5123

#SOCKET XOGADAS
xogadas = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#SOCKET ACTUALIZACIÓNS
actualizacions = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#INTENTANDO CONECTARSE AO SERVIDOR
print(u"Conectandose ao servidor...",[HOST,PORT])
try:
	xogadas.connect((HOST, PORT))
	xogadas.send(json.dumps(0))
except:
	print(u"Imposible conectar!")
	sys.exit()
	
print(u"...Conectado!")

#RECIVINDO A ID CORRESPONDENTE DO SERVIDOR
print(u"recibindo ID de xogador...")
try:
	s = xogadas.recv(1024)
	xogador = json.loads(s)
	print "ID: "+str(xogador)
except:
	print(u"Error na conexión!")
	sys.exit()
	
#CONECTANDO O SOCKET ACTUALIZACIÓNS
print(u"conectando socket 'actualizacións'...")
try:
	actualizacions.connect((HOST, PORT))
	actualizacions.sendall(json.dumps(xogador))
except:
	print(u"Non foi posible conectar o socket 'actualizacións'")
	sys.exit()
print(u"...Conectado!")
	
data = actualizacions.recv(1024)
lista_casillas,turno = json.loads(data)

print "casilla: "+str(lista_casillas), "turno: "+str(turno)

print u"Esperando a que os 2 xogadores estean conectados..."
data = actualizacions.recv(1024)
if json.loads(data) == "inicio":
	print u"Empeza o xogo!"
else:
	print u"Aconteceu un error!"
	sys.exit()

actualizacions.setblocking(0)

#CONSTANTES 
ANCHO_CADRO = 85
ALTO_CADRO = 85

MARCO = 15

GROSOR_LINHA = 2

COLOR_FONDO = [255,255,255]
COLOR_LINHAS = [80,80,80]
COLOR_1 = [0,0,100]
COLOR_2 = [200,0,0]
COLOR_VICTORIA = [100,200,100]

ANCHO_VENTANA = ANCHO_CADRO*3 + MARCO*2
ALTO_VENTANA = ALTO_CADRO*3 + MARCO*2
    
#XOGO

lista_casillas = [[0,0,0],[0,0,0],[0,0,0]]

ganhador = False
casilla_rato = False


pygame.init()
ventana = pygame.display.set_mode([ANCHO_VENTANA, ALTO_VENTANA])
font = pygame.font.SysFont("System", ANCHO_VENTANA/5)
font_turno = pygame.font.SysFont("System", ANCHO_VENTANA/15)

on = True

while on:

	reloj = pygame.time.Clock()

	#CONEXION
	
	try:
		data = actualizacions.recv(1024)
		print u"Recivido actualización: "+repr(data)
		lista_casillas,turno,ganhador,lista_colores = json.loads(data)
	except socket.error:
		pass
	
	#DEBUXAR
	
	ventana.fill(COLOR_FONDO)
	
	if xogador == turno and not ganhador:
		tocache = font_turno.render("tocache", 1, [0,0,0])
		ventana.blit(tocache, [0,0])
	elif ganhador and ganhador == xogador:
		ganhaches = font_turno.render("ganhaches!", 1, [50,200,50])
		ventana.blit(ganhaches, [0,0])
	elif ganhador and not ganhador == xogador:
		perdeches = font_turno.render("perdeches!", 1, [200,50,50])
		ventana.blit(perdeches, [0,0])
	
	rect_xogo = pygame.Rect(MARCO, MARCO, ANCHO_VENTANA-(MARCO*2), ALTO_VENTANA-(MARCO*2))
	pygame.draw.rect(ventana, [250,250,250], rect_xogo)
	
	
	for linha in range(len(lista_casillas)):
		for casilla in range(len(lista_casillas[linha])):
			#DEBUXAR SELECCIÓN
			if casilla_rato == [casilla,linha]:
				rect_sel = pygame.Rect(MARCO+ANCHO_CADRO*casilla, MARCO+ALTO_CADRO*linha, 
										ANCHO_CADRO, ALTO_CADRO)
				pygame.draw.rect(ventana, [240,240,240], rect_sel)
			#DEBUXAR GAÑADORES
			if ganhador and lista_colores[linha][casilla] == ganhador:
				rect_ganhador = pygame.Rect(MARCO+ANCHO_CADRO*casilla, MARCO+ALTO_CADRO*linha, 
											ANCHO_CADRO, ALTO_CADRO)
				pygame.draw.rect(ventana, COLOR_VICTORIA, rect_ganhador)
			#DEBUXAR SÍMBOLOS
			if lista_casillas[linha][casilla]:
				if lista_casillas[linha][casilla] == 1:
					simbolo = font.render("X", 1, COLOR_1)
				else:
					simbolo = font.render("O", 1, COLOR_2)
				ventana.blit(simbolo, [(MARCO+ANCHO_CADRO*casilla)+(ANCHO_CADRO/2)-simbolo.get_width()/2,
										(MARCO+ALTO_CADRO*linha)+(ALTO_CADRO/2)-simbolo.get_height()/2])

	for i in range(4):
		pygame.draw.line(ventana, COLOR_LINHAS, [MARCO, MARCO+i*ALTO_CADRO],
						[ANCHO_VENTANA-MARCO, MARCO+i*ALTO_CADRO], GROSOR_LINHA)
		pygame.draw.line(ventana, COLOR_LINHAS, [MARCO+i*ANCHO_CADRO, MARCO],
						[MARCO+i*ANCHO_CADRO, ALTO_VENTANA-(MARCO)], GROSOR_LINHA)
	
	#UPDATE DA PANTALLA
	
	pygame.display.update()
	
	#MOUSE
	
	pos_mouse = pygame.mouse.get_pos()
	if (MARCO < pos_mouse[0] < ANCHO_VENTANA-MARCO
		and MARCO < pos_mouse[1] < ALTO_VENTANA-(MARCO)):
		casilla_rato = [(pos_mouse[0]-MARCO)/ANCHO_CADRO,(pos_mouse[1]-MARCO)/ALTO_CADRO]
	else:
		casilla_rato = False
	
	#ACCIÓN E ENVIO DE DATOS
	
	if (not ganhador) and casilla_rato and pygame.mouse.get_pressed()[0]:
		if not lista_casillas[casilla_rato[1]][casilla_rato[0]]:
			if xogador == turno:
				print "xogador: "+str(xogador), "turno: "+str(turno)
				if xogador == turno:
					ENVIO = [casilla_rato[0],casilla_rato[1]]
					xogadas.sendall(json.dumps(ENVIO))
					print("send:",ENVIO)
	
	#EVENTOS
	
	for evento in pygame.event.get():
	
		#EXIT
		
		if evento.type == pygame.QUIT:
			pygame.display.quit()
			on = False
			actualizacions.close()
			xogadas.close()
	
	reloj.tick(60)
