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

    def saveEntitiesWatson(self, entityName, entitiesList, baseList=None, export=False):
        '''
            Genera lista de entidades para ser exportada a archivo CSV con
            formato capas de ser importado al servicio Watson.Conversation.

        :param entityName: nombre de la entidad, primera columna de archivo csv.
        :param entitiesList: lista de ejemplos para la misma entidad.
        :param baseList: lista previa que puede contener otras entidades a ser exportadas.
        :param export: default False, que indica si se debe exportar a archivo.
        :return: lista de entidades
        '''

        if baseList is None:
            entities = []
        else:
            entities = baseList

        for basic in entitiesList:
            if basic == '.':
                continue
            row = [entityName, basic]
            row = self.nlpProcess(row, basic)
            entities.append(row)

        if export:
            entitiesFile = open('entities.csv', mode='wb')
            writer = csv.writer(entitiesFile, dialect='excel', encoding='utf-8')
            writer.writerows(entities)

        return entities

    def saveEntitiesApiAI(self, entityName, entities, export=True):
        '''
            Prepara lista de entidades y exporta a archivo CSV compatible
            con API.AI.

        :param entityName: nombre de la entidad, nombre del archivo a exportar.
        :param entities: lista de ejemplos a ser exportados.
        :param export: default true, indica si se exporta archivo.
        :return: lista.
        '''
        ents = []
        for basic in entities:
            if basic == '.':
                continue
            row = [basic, basic]
            row = self.nlpProcess(row, basic)
            ents.append(row)

        if export:
            entsFile = open(entityName, mode='wb')
            writer = csv.writer(entsFile, dialect=csv.excel, encoding='utf-8', quoting=csv.QUOTE_ALL)
            writer.writerows(ents)
        return ents

    def nlpProcess(self, row, example):
        '''
            Función que expande la escritura de un exemplo via algunos cambios
            en el simbolo original: acentos, mayusculas y minúsculas, titulo

        :param row: lista en donde se agregan las expansiones
        :param example: simbolo base sobre el cual se trabaja
        :return: lista expandida.
        '''
        row.append(example.lower())
        row.append(example.upper())
        if example.title() != example:
            row.append(example.title())
        # replace latin
        noAcentos = self.noTilde(example)
        if example != noAcentos:
            row.append(noAcentos)
            row.append(noAcentos.lower())
            row.append(noAcentos.upper())
            if noAcentos.title() != noAcentos:
                row.append(noAcentos.title())
        return row

    def cleanText(self, originalText):
        temp = originalText.replace('&aacute;', 'á')
        temp = temp.replace('&Aacute;', 'Á')
        temp = temp.replace('&eacute;', 'é')
        temp = temp.replace('&Eacute;', 'É')
        temp = temp.replace('&iacute;', 'í')
        temp = temp.replace('&oacute;', 'ó')
        temp = temp.replace('&uacute;', 'ú')
        temp = temp.replace('&ntilde;', 'ñ')
        temp = temp.replace('&ordm;', '°')
        temp = temp.replace('&auml;', 'ä')
        temp = temp.replace('&Auml;', 'Ä')
        temp = temp.replace('&uuml;', 'ü')
        temp = temp.replace('&Uuml;', 'ü')
        temp = temp.replace('&agrave;', 'à')
        temp = temp.replace('&egrave;', 'è')
        temp = temp.replace('&amp;', '&')
        temp = temp.replace('  ', ' ')
        return temp

    def noTilde(self, originalText):
        temp = originalText.replace('á', 'a')
        temp = temp.replace('Á', 'A')
        temp = temp.replace('É', 'E')
        temp = temp.replace('é', 'e')
        temp = temp.replace('í', 'i')
        temp = temp.replace('Í', 'I')
        temp = temp.replace('ó', 'o')
        temp = temp.replace('Ó', 'O')
        temp = temp.replace('ú', 'u')
        temp = temp.replace('Ú', 'U')
        temp = temp.replace('ñ', 'n')
        temp = temp.replace('Ñ', 'N')
        temp = temp.replace('ü', 'u')
        temp = temp.replace('Ü', 'U')
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


