#!/usr/bin/python
# -*- coding: utf-8 -*-
#Copyright 2016 Nectia Think, Andres Gibson

import scraping
import re
import requests
import json


class JumboCl(scraping.Scraper):

    def __init__(self):
        scraping.Scraper.__init__(self)

        # Jumbo.cl Data
        self.entryPoint = 'http://www.jumbo.cl/FO/CategoryDisplay?cab=4008'
        self.headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'es-419,es;q=0.8,en-US;q=0.6,en;q=0.4',
                   'Connection': 'keep-alive',
                   'Host': 'www.jumbo.cl', 'Referer': 'http://www.jumbo.cl/FO/CategoryDisplay',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                   'X-Requested-With': 'XMLHttpRequest'}
        self.cookie = None

        # URLs
        # prods = requests.get('http://www.jumbo.cl/FO/PasoDosPub', params={'cab':4008, 'int':-1}, headers=h)
        # items = http://www.jumbo.cl/FO/PasoDosResultado?cab=4008&int=3789&ter=3786
        self.jumboCabs = range(4006, 4016)  # 4006-4015
        self.uriProds = 'http://www.jumbo.cl/FO/PasoDosPub'
        self.puriProds = {'cab': 4008, 'int': -1}
        self.uriItems = 'http://www.jumbo.cl/FO/PasoDosResultado'
        self.puriItems = {'cab': 4008, 'int': -1, 'ter': -1}

        # Regex
        # cab,int,ter, nombre
        self.reProds = '.+<a.+mostrarterminal\D+(\d+),(\d+),(\d+).+>(.+)</a>'
        # cid, nombre
        self.reMarcas = 'value="(\d+).+>(.+)<'

        # imagen, marca, producto, embase, precio x unidad, precio x medida estandar
        self.reData = re.compile('src="(/FO_IMGS/gr[^{"]+)".+?txt_marca_h.+?>([^<]+).+?<b>(.+?)</b>.+?<br.?>(.+?)[,|<].+?txt_precio_h.+?>(.+?) .+?precio_medida_h.+?>(.+?)<', re.DOTALL)
        # marca, producto
        self.reDataSimplidicada = 'txt_marca_h.+?>([^<]+).+?<b>(.+?)</b>'

        self.marcas = []
        self.productos = []
        self.items = []
        self.obtainCookie()

    def obtainCookie(self):
        print "Obtiene Cookie: ",
        r = requests.get(self.entryPoint);
        self.cookie = r.cookies
        print r.cookies['JSESSIONID']

    def catalogNavegationParams(self, uri, params, headers, regex):
        """ Obtiene parametros de navegación entre páginas del catálogo de productos.

            :param:uri: url desde donde es posible obtener lista de categorias.
            :param:params: parametros a enviar a página (url anterior).
            :param:headers: configuración de encabezado requerido por el servidor.
            :param:regex: expresión regular que permitirá obtener nombre de la categoría
                          y parámetros para navegar a ella
        """
        p = re.compile(regex)
        products = []
        for cab in self.jumboCabs:
            params['cab'] = cab
            r = requests.get(uri, params=params, headers=headers, cookies=self.cookie)
            products += re.findall(p, self.cleanText(r.content))
        return products

    def loadBrandProduct(self, arrProductos, uri, params, headers):
            relevant = scraping.ItemRecognizer('div', ('class', 'modulo_producto_vertical'), self.itemDataRecognize)
            try:
                for p in arrProductos:
                    params['int'] = p[1]
                    params['ter'] = p[2]
                    itemsContent = requests.get(uri, params=params, headers=headers, cookies=self.cookie)
                    print '\n- - -'  # , chardet.detect(p[3])
                    print u'Categoria Productos: ', p[3]
                    relevant.feed(itemsContent.content.replace('\n', '').replace('\t', ''))
                    relevant.resetCounter()
            except:
                # todo try to recover
                print 'err'
                raise

            return self.marcas, self.productos, self.items

    def itemDataRecognize(self, strWork):
        items = re.findall(self.reData, strWork)
        if len(items) > 0:
            imagen = self.cleanText(items[0][0].strip())
            marca = self.cleanText(items[0][1].strip())
            producto = self.cleanText(items[0][2].strip())
            embase = self.cleanText(items[0][3].strip())
            precioEmbase = self.cleanText(items[0][4].strip())
            precioEstandar = self.cleanText(items[0][5].strip())

            item = {
                'marca': marca,
                'producto': producto,
                'imagen': imagen,
                'embase': embase,
                'precioEmbase': precioEmbase,
                'precioEstandar': precioEstandar
            }

            if marca not in self.marcas:
                self.marcas.append(marca)
                print 'm',

            if producto not in self.productos:
                self.productos.append(producto)
                print 'p',

            if item not in self.items:
                self.items.append(item)
        else:
            print '-',


if __name__ == '__main__':

    scraper = JumboCl()

    print 'Carga Categorias: ',
    categoriesNav = scraper.catalogNavegationParams(scraper.uriProds, scraper.puriProds,
                                                    scraper.headers, scraper.reProds)
    print len(categoriesNav)
    print 'Carga Productos y Marcas: ',
    marcas, productos, items = scraper.loadBrandProduct(categoriesNav, scraper.uriItems, scraper.puriItems,
                                                        scraper.headers)

    prodFile = open('productos.json', 'wb')
    json.dump(productos, prodFile)

    marcasFile = open('marcas.json', 'wb')
    json.dump(marcas, marcasFile)

    itemsFile = open('items.json', 'wb')
    json.dump(items, itemsFile)

    prodFile.close()
    marcasFile.close()
    itemsFile.close()

    watsonEntities = scraper.saveEntitiesWatson("productos", productos, baseList=None, export=False)
    watsonEntities = scraper.saveEntitiesWatson("marcas", productos, baseList=watsonEntities, export=True)

    # (productos, marcas)
    scraper.saveEntitiesApiAI('producto', productos)
    scraper.saveEntitiesApiAI('marca', marcas)
