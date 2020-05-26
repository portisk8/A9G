import serial
import threading
import time
import re
import pynmea2
from random import getrandbits
from  builtins import any as b_any

debug=False
wordsToPrint = ['CALL','SOUNDER','RING']
class A9G(object):
	""" """


	def __init__(self,port):
		self.port = port
		self.comPort = serial.Serial \
				(
					port=port,
					baudrate=115200,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					bytesize=serial.EIGHTBITS
				)
		self.receive = threading.Thread(target=self.__receiveThread, name='ListenPort')
		self.receive.start()
		self.recuperarMensaje=None
		self.mensajeRecuperado=None
	
	def __receiveThread(self):
		'Hilo donde se imprimen los mensajes entrantes'
		while self.comPort:
			if self.comPort.inWaiting() > 0:
				c = self.comPort.readline()
				if(self.recuperarMensaje != None and self.recuperarMensaje in c.decode()): #En el caso de que se precise recuperar un mensaje
					self.mensajeRecuperado=c.decode()
				if(b_any( x in c.decode() for x in wordsToPrint)): print(c.decode())
			else:
				time.sleep(0.1)

	def __sendCommand(self,command):
		"""Envía comando AT.
		Parámetros:
			command -- Comando AT ej: AT+CGSN para ver el IMEI
		"""
		commandFormatEncoded = "{}\r".format(command).encode()
		self.comPort.write(commandFormatEncoded)
		time.sleep(1)
	def __sendCommandEspecial(self):
		'Envía el comando especial en bytes el hexadecimal 0x1a'
		self.comPort.write(bytes([26]))
		time.sleep(1)

	def isOk(self):
		'Sirve para verificar conexion con modulo A9G.'
		self.__sendCommand("AT")

	def callTo(self,phoneNumber):
		"""Realiza una llamada.\n
		Parámetros:
			phoneNumber -- numero de telefono ej: +549XXXXXXXXXX
		"""
		command = "ATD{}".format(phoneNumber)
		self.__sendCommand(command)

	def sendText(self,phoneNumber,text):
		"""Envía un mensaje de texto.\n
		Parámetros:
			phoneNumber -- numero de telefono ej: +549XXXXXXXXXX
			text		-- texto que desea enviar
		"""
		firstCommand = "AT+CMGF=1"
		self.__sendCommand(firstCommand)
		secondCommand = "AT+CMGS=\"{}\"".format(phoneNumber)
		self.__sendCommand(secondCommand)
		time.sleep(0.5)
		thirdCommand = '{}'.format(text)
		self.__sendCommand(thirdCommand)
		time.sleep(0.5)
		self.__sendCommandEspecial()
		# while self.mensajeRecuperado== None:
		# 	pass
		# numberStorageMessage = int(re.search(r'\d+', self.mensajeRecuperado).group()) #Recuperar un numero desde un string
		# self.mensajeRecuperado = None
		# self.recuperarMensaje = None
		# fourthCommand = 'AT+CMSS={}'.format(numberStorageMessage)
		# self.__sendCommand(fourthCommand)

	def answerPhone(self):
		'Contestar una llamada.'
		command = "ATA"
		self.__sendCommand(command)

	def ringOff(self):
		'Colgar una llamada.'
		command = "ATH"
		self.__sendCommand(command)

	def mqttConnect(self,host,port,user,password):
		"""Conectar a broker MQTT.\n
		Parámetros:
			host		-- Host/server del broker MQTT ej: "xx.cloudmqtt.com" 
			port		-- puerto del broker MQTT ej:"11519"
			user		-- usuario 
			password	-- password 
		"""
		command="AT+CGATT=1"
		self.__sendCommand(command)
		command="AT+CGDCONT=1,\"IP\",\"CMNET\""
		self.__sendCommand(command)
		command="AT+CGACT=1,1"
		self.__sendCommand(command)
		"""AT+MQTTCONN=<host>,
						<port>,<clientid>,
						<keepalive>,
						<cleansession>,
						[username],[password]
		"""
		command = "AT+MQTTCONN=\"{}\",{},\"12345\",120,0,\"{}\",\"{}\"".format(host,port,user,password)

	def mqttPublish(self,topic,msj):
		"""Publicar mensaje a broker MQTT.\n
		Parámetros:
			topic		-- topico que desea enviar el msj. ej: "/test" 
			msj		-- mensaje. ej:"Hello World!"
		"""
		command="AT+MQTTPUB=\"{}\",\"{}\",0,0,0".format(topic,msj)
		self.__sendCommand(command)

	def mqttSuscribe(self,topic):
		"""Suscribirse a un topico.\n
		Parámetros:
			topic		-- topico que desea suscribirse. ej: "/test" 
		"""
		command="AT+MQTTSUB=\"{}\",1,0".format(topic)
		self.__sendCommand(command)

	def mqttDisconnect(self):
		'Desconectarse del broker.'
		command="AT+MQTTDISCONN"
		self.__sendCommand(command)
		
	def gpsConnect(self,activarRastreo=False):
		'Encender el GPS.'
		command="AT+GPS=1"
		self.__sendCommand(command)
		if(activarRastreo):
			command="AT+GPSRD=1"
			self.__sendCommand(command)

	def gpsDisconnect(self,activarRastreo=False):
		'Apagar el GPS.'
		command="AT+GPS=0"
		self.__sendCommand(command)
		command="AT+GPSRD=0"
		self.__sendCommand(command)

	def gpsGetLocation(self):
		'Obtener Localización actual del GPS.'
		self.mensajeRecuperado = None
		self.recuperarMensaje="GNGGA"
		while self.recuperarMensaje != None:
			try:
				while (self.mensajeRecuperado == None):
					pass
				msgClean = self.mensajeRecuperado[7::] if "GNGGA" in self.mensajeRecuperado else self.mensajeRecuperado
				latlon = self.__getLocationFromMessage(msgClean)
				self.mensajeRecuperado = None
				self.recuperarMensaje = None
			except:
				self.recuperarMensaje = "GNGGA" if bool(getrandbits(1)) else "GNRMC"
				pass
		return latlon

	def convertToDecimalDegrees(self, value, multiplier):
		DD = float(value)/100
		return DD * multiplier

	def __getLocationFromMessage(self, msg):
		latLng = pynmea2.parse(msg)
		return latLng.latitude, latLng.longitude

	
		