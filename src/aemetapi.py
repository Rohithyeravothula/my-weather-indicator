#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# A library for access to AEMET Weather Service
#
# Copyright (C) 2017 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from comun import AEMETDB
import sqlite3
# -*- coding: UTF-8-*-
from xml.etree.ElementTree import parse
from urllib.request import urlopen
import datetime
import math
import time
import ssl


class Base:
    def __init__(self, url):
        self.rss = ''
        self.fecha = ''
        self.__url = url
        self.__fecha_de_actualizacion = ''
        self.__localidad = ''
        self.__provincia = ''
        self.precipitacion = []
        self.cota_nieve = []
        self.estado_cielo = []
        self.viento = []
        self.racha = []
        self.temperatura_maxima = 0
        self.temperatura_minima = 0
        self.temperatura_horas = []
        self.sensacion_termica_maxima = 0
        self.sensacion_termica_minima = 0
        self.sensacion_termica = []
        self.humedad_maxima = 0
        self.humedad_minima = 0
        self.humedad = []
        self.uv_max = 0

        self.__load_xml()

    def __load_xml(self):
        self.rss = parse(urlopen(self.__url)).getroot()

        self.__load_datos_base()

    def __load_datos_base(self):
        self.__fecha_de_actualizacion = self.rss.find(
            'elaborado').text
        self.__localidad = self.rss.find('nombre').text
        self.__provincia = self.rss.find('provincia').text

    '''Interfaz publica'''
    def get_fecha_actualizacion(self):
        return self.__fecha_de_actualizacion

    def get_localidad(self):
        return self.__localidad

    def get_provincia(self):
        return self.__provincia

    def get_precipitacion(self):
        return self.precipitacion

    def get_cota_nieve(self):
        return self.cota_nieve

    def get_estado_cielo(self):
        return self.estado_cielo

    def get_viento(self):
        return self.viento

    def get_racha(self):
        return self.racha

    def get_temperatura_maxima(self):
        return self.temperatura_maxima

    def get_temperatura_minima(self):
        return self.temperatura_minima

    def get_temperatura_horas(self):
        return self.temperatura_horas

    def get_sensacion_termica_maxima(self):
        return self.sensacion_termica_maxima

    def get_sensacion_termica_minima(self):
        return self.sensacion_termica_minima

    def get_sensacion_termica(self):
        return self.sensacion_termica

    def get_humedad_maxima(self):
        return self.humedad_maxima

    def get_humedad_minima(self):
        return self.humedad_minima

    def get_humedad(self):
        return self.humedad

    def get_uv_max(self):
        return self.uv_max


class Localidad(Base):

    '''Fecha en formato dd/mm/AAAA'''
    def __init__(self, codigo_postal, fecha):
        url = ('http://www.aemet.es/xml/municipios/localidad_' +
               codigo_postal + '.xml')
        print(url)
        Base.__init__(self, url)
        self.fecha = datetime.datetime.strptime(
            fecha, '%d/%m/%Y').strftime('%Y-%m-%d')
        self.__load_datos(self.fecha)

    '''Carga de los datos del XML para el dia seleccionado'''
    def __load_datos(self, fecha):
        nodo = self.rss.find("prediccion/dia[@fecha='" + fecha + "']")
        if nodo is not None:
            '''Probabilidad de precipitacion'''
            for elem in nodo.findall('prob_precipitacion'):
                self.precipitacion.append([elem.get('periodo'), elem.text])

            '''Cota de nieve'''
            for elem in nodo.findall('cota_nieve_prov'):
                self.cota_nieve.append([elem.get('periodo'), elem.text])

            '''Estado'''
            for elem in nodo.findall('estado_cielo'):
                self.estado_cielo.append(
                    [elem.get('periodo'), elem.get('descripcion')])

            '''Viento'''
            for elem in nodo.findall('viento'):
                self.viento.append([elem.get('periodo'),
                                    elem.find('direccion').text,
                                    elem.find('velocidad').text])

            '''Racha maxima'''
            for elem in nodo.findall('racha_max'):
                self.racha.append([elem.get('periodo'), elem.text])

            '''Temperaturas'''
            self.temperatura_maxima = nodo.find('temperatura/maxima').text
            self.temperatura_minima = nodo.find('temperatura/minima').text

            for elem in nodo.findall('temperatura/dato'):
                self.temperatura_horas.append([elem.get('hora'), elem.text])

            '''Sensacion termica'''
            self.sensacion_termica_maxima = nodo.find('sens_termica/maxima').text
            self.sensacion_termica_minima = nodo.find('sens_termica/minima').text

            for elem in nodo.findall('sens_termica/dato'):
                self.sensacion_termica.append([elem.get('hora'), elem.text])

            '''Humedad'''
            self.humedad_maxima = nodo.find('humedad_relativa/maxima').text
            self.humedad_minima = nodo.find('humedad_relativa/minima').text

            for elem in nodo.findall('humedad_relativa/dato'):
                self.humedad.append([elem.get('hora'), elem.text])

            '''U.V. Maximo'''
            self.uv_max = nodo.find('uv_max').text


def dist(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_r = lat1 * math.pi/360.0
    lat2_r = lat2 * math.pi/360.0
    lon1_r = lon1 * math.pi/360.0
    lon2_r = lon2 * math.pi/360.0
    delta_lat = (lat2_r - lat1_r)
    delta_lon = (lon2_r - lon1_r)
    a = (math.pow(math.sin(delta_lat/2.0), 2.0) +
         math.cos(lat1_r) * math.cos(lat2_r) *
         math.pow(math.sin(delta_lon/2.0), 2.0))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

if __name__ == '__main__':
    print(AEMETDB)
    lat = 39.3527902
    lon = -0.4016816
    # lat = 39.3328701015343
    # lon = -1.3254618644714355
    sqlstring = """
SELECT ID, LATITUD, LONGITUD, IDAEMET,
MIN((LATITUD+{0})*(LATITUD+{0}) +
(LONGITUD+{1})*(LONGITUD+{1})) FROM SPAIN_FORECASTING_CITIES;
""".format(-lat, -lon)
    print(sqlstring)
    conn = sqlite3.connect(AEMETDB)
    c = conn.cursor()
    c.execute(sqlstring)
    answer = c.fetchone()
    print(answer)
    print(dist(lat, lon, answer[1], answer[2]))
    print(time.strftime("%d/%m/%Y"))
    sqlstring = """
SELECT ID, LATITUD, LONGITUD, IDAEMET,
MIN((LATITUD+{0})*(LATITUD+{0}) +
(LONGITUD+{1})*(LONGITUD+{1})) FROM SPAIN_OBSERVATION_CITIES;
""".format(-lat, -lon)

    print(sqlstring)
    conn = sqlite3.connect(AEMETDB)
    c = conn.cursor()
    c.execute(sqlstring)
    answer2 = c.fetchone()
    print(answer2)
    print(dist(lat, lon, answer2[1], answer2[2]))
    print(time.strftime("%d/%m/%Y"))
    print('---', answer2[3], '---')
    url = 'http://www.aemet.es/es/eltiempo/observacion/ultimosdatos?k=val&l=%s&w=0&datos=det&x=h24&f=temperatura' % answer2[3]
    print(url)
    url = 'http://www.aemet.es/es/eltiempo/observacion/ultimosdatos_{0}_datos-horarios.csv?k=val&l={0}&datos=det&w=0&f=temperatura&x='.format(answer2[3])
    print(url)
    response = urlopen(url)
    print(response.status)
    data = response.read().decode('ISO-8859-15')
    print(data)
    import csv
    from io import StringIO
    f = StringIO(data)
    reader = csv.reader(f, delimiter=',')
    data = []
    values = []
    for index, row in enumerate(reader):
        if index == 3:
            values = row
        elif index > 3:
            mr = {}
            for index, value in enumerate(values):
                mr[value] = row[index]
            data.append(mr)
    print(data)
    tiempo = Localidad(answer[3], '27/01/2017')
    print('27/01/2017')
    print('Localidad: ', tiempo.get_localidad())
    print('Temp. max:', tiempo.get_temperatura_maxima())
    print('Temp. min:', tiempo.get_temperatura_minima())
    print('Precipitación:', tiempo.get_precipitacion())
    print('Temperatura:', tiempo.get_temperatura_horas())
    tiempo = Localidad(answer[3], '28/01/2017')
    print('28/01/2017')
    print('Localidad: ', tiempo.get_localidad())
    print('Temp. max:', tiempo.get_temperatura_maxima())
    print('Temp. min:', tiempo.get_temperatura_minima())
    print('Precipitación:', tiempo.get_precipitacion())
    print('Temperatura:', tiempo.get_temperatura_horas())
    '''
    print('---------------------')
    APIKEY = """eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsb3JlbnpvLmNhcmJvbmVsbC5jZXJlem9AZ21haWwuY29tIiwianRpIjoiNmU1ZjRkYjktNDE3Yi00MTRiLWEwMjctNDM3MWVkMzliNWE1IiwiZXhwIjoxNDkyNzE4NDY0LCJpc3MiOiJBRU1FVCIsImlhdCI6MTQ4NDk0MjQ2NCwidXNlcklkIjoiNmU1ZjRkYjktNDE3Yi00MTRiLWEwMjctNDM3MWVkMzliNWE1Iiwicm9sZSI6IiJ9.iXv7EcPcF3iuE78u_qqZpxHj1Whg-svH5-aO4S01_W4"""
    headers = {'Accept': 'text/plain',
               'api_key': APIKEY,
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
               'Content-Type': 'application/json'}
    import requests
    url = "https://opendata.aemet.es/opendata/api/prediccion/nacional/medioplazo"
    #ans = requests.get(url, headers=headers, verify=False)
    #print(ans.text)

    import urllib.parse
    import urllib.request
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'Accept': 'text/plain',
               'api_key': APIKEY,
               'User-Agent': user_agent,
               'Content-Type': 'application/json'}
    # req = urllib.request.Request(url, headers, unverifiable=True)
    with urllib.request.urlopen(url) as response:
        the_page = response.read()
    import codecs
    import json
    afile = codecs.open('/home/lorenzo/data.json', 'r', 'ISO-8859-15')
    data = afile.read()
    afile.close()
    print(data)
    fjson = json.loads(data)
    print(fjson)
    import csv
        csvfile = codecs.open('/home/lorenzo/.json', 'w', 'utf-8')
    writer = csv.writer(csvfile)
    for element in fjson:
        writer.writerow([element['idema'], element['ubi'], element['lat'], element['lon'], element['alt']])
    csvfile.close()
    '''
