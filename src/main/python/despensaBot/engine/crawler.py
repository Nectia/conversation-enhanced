#!/usr/bin/python
# -*- coding: utf-8 -*-
#Copyright 2016 Nectia Think, Andres Gibson

import requests
import re
import json
import csv
import codecs

# Jumbo.cl Data
# Header requiere ser obtenido primero utilizando browser en pagina
# http://www.jumbo.cl/FO/CategoryDisplay , luego reemplazar propiedad
# Cookie. Es posible que al primer intento no se obtenga una sesion valida,
# F5-refresh y revisar nuevamente.
headers = {'Accept':'*/*', 'Accept-Encoding': 'gzip, deflate, sdch',
         'Accept-Language':'es-419,es;q=0.8,en-US;q=0.6,en;q=0.4',
         'Connection':'keep-alive',
         'Cookie':'style=null; __utma=91194497.676083743.1477606823.1478309223.1478460346.11; __utmc=91194497; __utmz=91194497.1477606823.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); JSESSIONID=0000T5bNKBP-riu50HmQOsnXsE-:-1; chaordic_browserId=8d6f8380-9c93-11e6-901d-17229d8f0cd9; chaordic_anonymousUserId=anon-8d6f8380-9c93-11e6-901d-17229d8f0cd9; chaordic_session=1478527573080-0.829889184539266; chaordic_testGroup=%7B%22experiment%22%3Anull%2C%22group%22%3Anull%2C%22testCode%22%3Anull%2C%22code%22%3Anull%2C%22session%22%3Anull%7D; queueit_js_jumbocl_cyberdayjumbo_userverified=verified',
         'Host':'www.jumbo.cl', 'Referer':'http://www.jumbo.cl/FO/CategoryDisplay',
         'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
         'X-Requested-With':'XMLHttpRequest'}

# Entities
entityProd = 'producto'
entityMarca = 'marca'

# URLs
# Jumbo.cl
# prods = requests.get('http://www.jumbo.cl/FO/PasoDosPub', params={'cab':4008, 'int':-1}, headers=h)
# items = http://www.jumbo.cl/FO/PasoDosResultado?cab=4008&int=3789&ter=3786
jumboCabs = range(4006, 4016)  # 4006-4015
uriProds = 'http://www.jumbo.cl/FO/PasoDosPub'
puriProds = {'cab': 4008, 'int': -1}
uriItems = 'http://www.jumbo.cl/FO/PasoDosResultado'
puriItems = {'cab': 4008, 'int': -1, 'ter': -1}

# Regex
# Jumbo.cl
# cab,int,ter, nombre
reProds = '.+<a.+mostrarterminal\D+(\d+),(\d+),(\d+).+>(.+)</a>'
# cid, nombre
reMarcas = 'value="(\d+).+>(.+)<'

# imagen, marca, producto, embase, precio x unidad, precio x medida estandar
reData = 'src="([^{"]+ST\.jpg)".+?txt_marca_h.+?>([^<]+).+?<b>(.+?)</b>.+?<br>(.+?)[,|<].+?txt_precio_h.+?>(.+?) .+?precio_medida_h.+?>(.+?)<'
# marca, producto
reDataSimplidicada = 'txt_marca_h.+?>([^<]+).+?<b>(.+?)</b>'



def itemsPorCategoria(arrProductos, uri=uriItems, params=puriItems, headers=headers, regex=reData):
    itemRE = re.compile(regex, re.DOTALL)
    marcas = []
    productos = []
    items = []
    try:
        for p in arrProductos:
            params['int'] = p[1]
            params['ter'] = p[2]
            itemsContent = requests.get(uri, params=params, headers=headers)
            print '\n- - -'  # , chardet.detect(p[3])
            print u'Categoria Productos: ', p[3]
            items = re.findall(itemRE, unicode(itemsContent.content, errors='replace'))
            print u'  Items: ',
            for i in items:
                imagen = i[0]
                marca = i[1]
                producto = i[2]
                embase = i[3]
                precioEmbase = i[4]
                precioEstandar = i[5]

                item = {
                    'marca': marca,
                    'producto': producto,
                    'imagen': imagen,
                    'embase': embase,
                    'precioEmbase': precioEmbase,
                    'precioEstandar': precioEstandar
                }

                if marca not in marcas:
                    marcas.append(marca)
                    print 'm',

                if producto not in productos:
                    productos.append(producto)
                    print 'p',

                if item not in items:
                    items.append(item)

    except:
        # todo try to recover
        print 'err'
        raise

    return marcas, productos, items

def itemsPorCategoriaSimplificada(arrProductos, uri=uriItems, params=puriItems, headers=headers, regex=reDataSimplidicada):
    itemRE = re.compile(regex, re.DOTALL)
    marcas = []
    productos = []
    items = []
    try:
        for p in arrProductos:
            params['int'] = p[1]
            params['ter'] = p[2]
            itemsContent = requests.get(uri, params=params, headers=headers)
            print '\n- - -'  # , chardet.detect(p[3])
            print u'Categoria Productos: ', p[3]
            itemsArr = re.findall(itemRE, cleanAcutes(unicode(itemsContent.content, errors='replace')))
            print u'  Items: ',
            for i in itemsArr:
                marca = i[0]
                producto = i[1]

                item = {
                    'marca': marca,
                    'producto': producto
                }

                if marca not in marcas:
                    marcas.append(marca)
                    print 'm',

                if producto not in productos:
                    productos.append(producto)
                    print 'p',

                if item not in items:
                    items.append(item)

    except:
        # todo try to recover
        print 'err'
        raise

    return marcas, productos, items

def cleanAcutes(originalText):
    temp = originalText.replace('&aacute;', 'a')
    temp = temp.replace('&eacute;', 'e')
    temp = temp.replace('&iacute;', 'i')
    temp = temp.replace('&oacute;', 'o')
    temp = temp.replace('&uacute;', 'u')
    temp = temp.replace('&ntilde;', 'n')
    temp = temp.replace('&ordm;', '°')
    return temp

def productosGenericos(uri=uriProds, params=puriProds, headers=headers, regex=reProds):
    p = re.compile(regex)
    products = []
    for cab in jumboCabs:
        params['cab'] = cab
        r = requests.get(uri, params=params, headers=headers)
        products += re.findall(p, unicode(r.content, errors='ignore'))
    return products

def marcasPorProducto(arrProductos, uri=uriItems, params=puriItems, headers=headers, regex=reMarcas):
    itemRE = re.compile(regex)
    marcas = []
    try:
        for p in arrProductos:
            params['int'] = p[1]
            params['ter'] = p[2]
            itemsContent = requests.get(uri, params=params, headers=headers)
            print '\n- - -'#, chardet.detect(p[3])
            print u'Producto: ', p[3]
            items = re.findall(itemRE,  unicode(itemsContent.content, errors='replace'))
            print u'  Marcas disponibles: ',
            for i in items:
                if i not in marcas:
                    print '+',
                    marcas.append(i)
                else:
                    print '.',

    except:
        # todo try to recover
        print 'err'
        raise

    return marcas

def saveEntities(productos, marcas):
    entities = []
    for p in productos:
        row = [entityProd, p]
        entities.append(row)

    for m in marcas:
        row = [entityMarca, m]
        entities.append(row)

    entitiesFile = codecs.open('entities.csv', mode='wb', encoding='utf-8')
    writer = csv.writer(entitiesFile)
    writer.writerows(entities)



if __name__ == '__main__':
    print 'Carga Categorias: ',
    prods = productosGenericos()
    print len(prods)
    print 'Carga Productos y Marcas: ',
    marcas, productos, items = itemsPorCategoriaSimplificada(prods)

    prodFile = open('productos.json', 'wb')
    json.dump(productos, prodFile)

    marcasFile = open('marcas.json', 'wb')
    json.dump(marcas, marcasFile)

    itemsFile = open('items.json', 'wb')
    json.dump(items, itemsFile)

    prodFile.close()
    marcasFile.close()
    itemsFile.close()

    saveEntities(productos, marcas)

