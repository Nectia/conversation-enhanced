#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2016 Nectia Think, Andres Gibson

from HTMLParser import HTMLParser
import codecs
import unicodecsv as csv

class Scraper():
    def __init__(self):
        self.productos = {}
        self.marcas = []
        self.ofertas = {}
        self.sinonimos = {}

        self.workingText = ''

        # Entities
        self.entityProd = 'producto'
        self.entityMarca = 'marca'

    def producto(self):
        """ Definición de un producto

            name: nombre unico del producto
            brand: nombre canonico de la marca
            code: codigo identificador de producto en tienda fuente.
            imageURL: parte del path a partir de raíz conocida por el
                    sistema, en donde la fuente publica una imagen del
                    producto.
            unitPrice: precio que posee la unidad de venta. Ejemplo: $2.000 botella de 1.5 ltrs.
            standardPrice: precio por el cual se compara un producto con otro, a similar volumen
                            o masa u otra unidad con la cual se puedan comparar.
                            Ejemplo: $1.500 por litro.
            unitMetric: nombre de la unidad (entidad) con en la cual se vende el producto.
                        Ejemplo: Botella
            standardMetric: nombre de la unidad (entidad) con la cual se compara el producto.
                        Ejemplo: Litro
        """
        return {"name": None, "brand": None, "code": None, "imageURL": None,
                "unitPrice": 0, "standardPrice": 0, "sellUnit": None, "standardUnit": None}

    def oferta(self):
        """ Definicion de una oferta

            name: nombre de la oferta
            product: nombre canonico del producto
            brand: nombre canonico de la marca
            code: codigo con el cual la fuente identifica al item
            text: texto que pueda ser desplegado junto a la imagen del producto que describa
                    en que consiste la oferta.

        """
        return {"name": None, "product": None, "brand": None, "code": None, "text": None}


    def catalogNavegationParams(self, uri, params, headers, regex):
        """ Obtiene parametros de navegación entre páginas del catálogo de productos.

            :param:uri: url desde donde es posible obtener lista de categorias.
            :param:params: parametros a enviar a página (url anterior).
            :param:headers: configuración de encabezado requerido por el servidor.
            :param:regex: expresión regular que permitirá obtener nombre de la categoría
                          y parámetros para navegar a ella
        """
        raise Exception('Method must be implemented by children classes.')


    def saveEntities(self, productos, marcas):
        entities = []
        for p in productos:
            row = [self.entityProd, p]
            entities.append(row)

        for m in marcas:
            row = [self.entityMarca, m]
            entities.append(row)

        entitiesFile = open('entities.csv', mode='wb')
        writer = csv.writer(entitiesFile, dialect='excel', encoding='utf-8')
        writer.writerows(entities)

    def cleanText(self, originalText):
        temp = originalText.replace('&aacute;', 'á')
        temp = temp.replace('&eacute;', 'é')
        temp = temp.replace('&iacute;', 'í')
        temp = temp.replace('&oacute;', 'ó')
        temp = temp.replace('&uacute;', 'ú')
        temp = temp.replace('&ntilde;', 'ñ')
        temp = temp.replace('&ordm;', '°')
        temp = temp.replace('&auml;', 'ä')
        temp = temp.replace('&Auml;', 'Ä')
        temp = temp.replace('&agrave;', 'à')
        temp = temp.replace('&egrave;', 'è')
        return temp


class ItemRecognizer(HTMLParser):

    def __init__(self, startTag, searchProperty, callback):
        HTMLParser.__init__(self)
        self.startTag = startTag
        self.searchProperty = searchProperty
        self.deepCount = 0
        self.deepMark = -1
        self.startPos = 0
        self.endPos = 0
        self.callback = callback

    def resetCounter(self):
        self.deepCount = 0
        self.deepMark = -1
        self.reset()

    def handle_starttag(self, tag, attrs):
        if tag == self.startTag:
            try:
                attrs.index(self.searchProperty)
                self.startPos = self.getpos()[1]
                self.deepMark = self.deepCount
            except:
                pass
            finally:
                self.deepCount += 1


    def handle_endtag(self, tag):
        if tag == self.startTag:
            self.deepCount -= 1
            if self.deepCount == self.deepMark:
                self.endPos = self.getpos()[1]
                self.callback(self.rawdata[self.startPos:self.endPos])

if __name__ == '__main__':
    # Test ItemRecognizer
    def callback_print(txt):
        print txt

    f = open('rawdata.html', 'rb')

    parser = ItemRecognizer('div', ('class', 'modulo_producto_vertical'), callback_print)
    parser.feed(f.read())


