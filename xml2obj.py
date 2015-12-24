#!/usr/bin/env python2
# encoding: utf-8

import javaobj
import base64
from xml.dom import getDOMImplementation


class XmlUnMarshaller(object):
    def __init__(self, *args, **kwargs):
        self._references = []
        self.TAG_MAP = (
                ('object', )
        )


    def _lookup_and_exec(self, element):


    def unmarshall(self, fobj):
        obj = None

        return obj
