# -*- encoding: utf-8 -*-
import requests
import logging
from datetime import datetime
from io import StringIO
import io
from PIL import Image
from bs4 import BeautifulSoup
import time
import unicodedata
import os
import json

_logger = logging.getLogger(__name__)

def obtener_token(client_id, client_secret):
	endpoint = "https://api-seguridad.sunat.gob.pe/v1/clientessol/%s/oauth2/token/" % client_id
	headers = {
		"Content-Type": "application/x-www-form-urlencoded",
	}
	datos_json = {
		'grant_type': 'password',
		'scope': 'https://api-cpe.sunat.gob.pe',
		'client_id': client_id,
		'client_secret': client_secret,
		'username': '20605310321IQUIRGIO',
		'password': 'aptichelh',
	}
	datos_peticion = requests.post(endpoint, data=datos_json, headers=headers)
	if datos_peticion.status_code == 200:
		datos = datos_peticion.json()
		return datos
	else:
		return ""

def enviar_guia(client, document):
	#endpoint = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/{numRucEmisor}-{codCpe}-{numSerie}-{numCpe}"
	endpoint = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/%s-%s-%s-%s" % client_id
	headers = {
		"Content-Type": "application/x-www-form-urlencoded",
	}
	datos_archivo = {
		"nomArchivo": "",
		"arcGreZip": "",
		"hashZip": ""
	}
	datos_json = {
		'numRucEmisor': 'password',
		'codCpe': '09',
		'numSerie': client_id,
		'numCpe': client_secret,
		"archivo": datos_archivo,
	}
	datos_peticion = requests.post(endpoint, data=datos_json, headers=headers)
	if datos_peticion.status_code == 200:
		datos = datos_peticion.json()
		return datos
	else:
		return ""

rpt = obtener_token('b3c0fa04-2c15-4b85-90a7-af1edc2ce5ac', 'WjzTsVSW5xLaB2E9JL+tQw==')
token = rpt['access_token']
print("token")
print(token)

scope 
 <client_id> generado en menú SOL
 <client_secret> generado en menú SOL
username <Número de RUC> + <Usuario SOL>
password <Contraseña SOL>

# x-www-form-unrencoded
head = {'Content-Type' : 'application/x-www-form-urlencoded'}    
    auth_info = {'client_id' : "unit:"+api_params.id,
                'grant_type' : 'client_credentials',
                'client_secret' : api_params.secret,
                'scope' : 'unit',
                }