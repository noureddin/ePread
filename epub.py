# -*- coding: utf-8 -*-
# vim: set et sw=4 ts=4 :

import os
from zipfile import ZipFile
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

class EpubExtractor:

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.tmp = TemporaryDirectory()
        tmp = self.tmp.name
        #
        with ZipFile(self.path) as book:
            book.extractall(path=tmp)
        #
        opf = os.path.join(tmp, 'META-INF', 'container.xml')
        relative_content = ET.parse(opf).find('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile').get('full-path')
        content = os.path.join(tmp, relative_content)
        if not os.path.isabs(os.path.dirname(content)):
            content = os.path.join(os.getcwd(), content)
        rooturl = 'file://' + os.path.dirname(content).replace(os.path.sep, '/') + '/'
        #
        r = ET.parse(content).getroot()
        # get the urls for every page, given its id
        m = r.find('{http://www.idpf.org/2007/opf}manifest')
        id2href = { e.attrib['id']: e.attrib['href']  for e in m  if e.attrib['media-type']=="application/xhtml+xml" }
        # get the pages' ids (then hrefs) in order
        s = r.find('{http://www.idpf.org/2007/opf}spine')
        urls = [ rooturl + id2href[ e.attrib['idref'] ] for e in s ]
        # get title
        title = r.find('.//{http://purl.org/dc/elements/1.1/}title').text
        return title, urls


    def __exit__(self, exc, value, tb):
        self.tmp.cleanup()
