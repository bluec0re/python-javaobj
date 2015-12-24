#!/usr/bin/env python2
# encoding: utf-8

import javaobj
import base64
import logging
from javaobj import DefaultObjectTransformer
from xml.dom import getDOMImplementation

javaobj.JavaList = DefaultObjectTransformer.JavaList
javaobj.JavaMap = DefaultObjectTransformer.JavaMap

log = logging.getLogger(__name__)

class XmlMarshaller(object):
    def __init__(self, *args, **kwargs):
        """@todo: Docstring for __init__
        :obj: @todo
        :*args: @todo
        :**kwargs: @todo
        :returns: @todo
        """
        self.TYPE_MAP = (
            (javaobj.JavaArray, self.do_array),
            (javaobj.JavaMap, self.do_map),
            (javaobj.JavaList, self.do_list),
            (javaobj.JavaEnum, self.do_enum),
            (javaobj.JavaString, self.do_string),
            (javaobj.JavaObject, self.do_object),
            (javaobj.JavaClass, self.do_class),
            (javaobj.JavaProxyClass, self.do_proxyclass),
            (str, self.do_blockdata),
            (type(None), self.do_null),
        )

        self._references = []

        self.__create_doc()

    def __create_doc(self):
        self.__impl = getDOMImplementation()
        self.doc = self.__impl.createDocument(None, None, None)

    def _lookup_and_exec(self, obj):
        for typ, func in self.TYPE_MAP:
            if isinstance(obj, typ):
                log.debug('Object of type %s found' % str(typ))
                return func(obj)

        raise RuntimeError("No handler found for type %s (value %r)" % (type(obj), obj))

    def marshall(self, obj):
        self.__create_doc()
        root = self.doc.createElement('root')
        if not isinstance(obj, list):
            obj = list(obj)

        for o in obj:
            root.appendChild(self._lookup_and_exec(o))
        self.doc.appendChild(root)
        return self.doc.toprettyxml(indent='  ')

    def do_value(self, value):
        if isinstance(value, bool):
            return self.doc.createTextNode(str(value))
        elif isinstance(value, int):
            return self.doc.createTextNode(str(value))
        elif isinstance(value, float):
            return self.doc.createTextNode(str(value))
        else:
            return self._lookup_and_exec(value)

    def do_object(self, obj, annot_filter=None):
        if obj in self._references:
            ref = self.doc.createElement('reference')
            ref.setAttribute('idx', str(self._references.index(obj)))
            return ref

        ref = len(self._references)
        self._references.append(obj)

        obj_el = self.doc.createElement('object')
        obj_el.setAttribute('ref', str(ref))

        tmpcls = obj.get_class()
        if hasattr(tmpcls, 'fields_names'):
            obj_el.appendChild(self.do_class(tmpcls))
            field_names = []
            field_types = []
            while tmpcls:
                field_names += tmpcls.fields_names
                field_types += tmpcls.fields_types
                tmpcls = tmpcls.superclass

            lookup = dict(zip(field_names, field_types))
            fields_el = self.doc.createElement('fields')
            for field in field_names:
                field_el = self.doc.createElement('field')
                field_el.setAttribute('name', field)
                subel = None
                try:
                    value = getattr(obj, field)
                    subel = self.do_value(value)
                except AttributeError as e:
                    log.info('AttributeError: %s', str(e), exc_info=1)
                    subel = self.do_null()
                field_el.appendChild(subel)
                fields_el.appendChild(field_el)

            obj_el.appendChild(fields_el)
        elif hasattr(tmpcls, 'interface_names'):
            obj_el.appendChild(self.do_proxyclass(tmpcls))

        annotations_el = self.doc.createElement('annotations')
        for idx,annot in zip(range(len(obj.annotations)), obj.annotations):
            if annot_filter and not annot_filter(idx,annot):
                continue
            annot_el = self.doc.createElement('annotation')
            annot_el.appendChild(self._lookup_and_exec(annot))
            annotations_el.appendChild(annot_el)
        obj_el.appendChild(annotations_el)

        return obj_el
    
    def do_null(self, dummy=None):
        return self.doc.createComment('NULL')

    def do_string(self, obj):
        if obj in self._references:
            ref = self.doc.createElement('reference')
            ref.appendChild(self.doc.createComment(str(obj)))
            ref.setAttribute('idx', str(self._references.index(obj)))
            return ref

        ref = len(self._references)
        self._references.append(obj)
        str_el = self.doc.createElement('string')
        str_el.setAttribute('ref', str(ref))
        str_el.appendChild(self.doc.createTextNode(str(obj)))

        return str_el

    def do_class(self, cls):
        if cls in self._references:
            ref = self.doc.createElement('reference')
            ref.setAttribute('idx', str(self._references.index(cls)))
            return ref

        ref = len(self._references)
        self._references.append(cls)
        cls_el = self.doc.createElement('class')
        cls_el.setAttribute('ref', str(ref))
        cls_el.setAttribute('name', cls.name)
        cls_el.setAttribute('handle', hex(cls.handle))
        cls_el.setAttribute('serial', hex(cls.serialVersionUID))
        cls_el.setAttribute('flags', hex(cls.flags))

        if cls.superclass:
            scls = self.do_class(cls.superclass)
            scls.tagName = 'superclass'
            cls_el.appendChild(scls)

        fields = self.doc.createElement('fields')
        for name, typ in zip(cls.fields_names, cls.fields_types):
            field = self.doc.createElement('field')
            field.setAttribute('name', name)
            field.setAttribute('type', typ)
            fields.appendChild(field)
        cls_el.appendChild(fields)

        return cls_el


    def do_proxyclass(self, prxcls):
        if prxcls in self._references:
            ref = self.doc.createElement('reference')
            ref.setAttribute('idx', str(self._references.index(prxcls)))
            return ref

        ref = len(self._references)
        self._references.append(prxcls)
        cls_el = self.doc.createElement('proxyclass')
        cls_el.setAttribute('ref', str(ref))
        if prxcls.handle:
            cls_el.setAttribute('handle', hex(prxcls.handle))

        if prxcls.superclass:
            scls = self.do_class(prxcls.superclass)
            scls.tagName = 'superclass'
            cls_el.appendChild(scls)

        names = self.doc.createElement('proxyInterfaceNames')
        for name in prxcls.interface_names:
            el = self.doc.createElement('proxyInterfaceName')
            el.appendChild(self.doc.createTextNode(name))
            names.appendChild(el)
        cls_el.appendChild(names)

        return cls_el


    def do_blockdata(self, obj):
        try:
            if '\x00' in obj:
                raise UnicodeDecodeError("","",0,0,"")
            obj.decode('utf-8')
            return self.doc.createTextNode(obj)
        except UnicodeDecodeError:
            b64 = self.doc.createElement('base64')
            b64.appendChild(self.doc.createTextNode(base64.b64encode(obj)))
            return b64

    def do_array(self, obj):
        arr_el = self.do_object(obj)
        arr_el.tagName = 'array'

        items = self.doc.createElement('items')
        for i in obj:
            item = self.doc.createElement('item')
            
            if obj.classdesc.name[1] in ('L', '['):
                item.appendChild(self._lookup_and_exec(i))
            else:
                item.appendChild(self._do_value(obj.classdesc.name[1:], i))
            items.appendChild(item)

        
        arr_el.appendChild(items)


        return arr_el

    def do_map(self, obj):
        map_el = self.do_object(obj, lambda idx,ann: idx < 1)
        map_el.tagName = 'map'


        items = self.doc.createElement('items')
        for i in range(1, len(obj.annotations), 2):
            item = self.doc.createElement('item')
            item.setAttribute('name', str(obj.annotations[i]))
            item.appendChild(self._lookup_and_exec(obj.annotations[i+1]))
            items.appendChild(item)

        
        map_el.appendChild(items)


        return map_el

    def do_list(self, obj):
        list_el = self.do_object(obj, lambda idx,ann: idx < 1)
        list_el.tagName = 'list'
 
        items = self.doc.createElement('items')
        for i in range(1, len(obj.annotations)):
            item = self.doc.createElement('item')
            item.appendChild(self._lookup_and_exec(obj.annotations[i]))
            items.appendChild(item)

        
        list_el.appendChild(items)
        return list_el

    def do_enum(self, obj):
        return self.doc.createComment('enum')

    def _do_value(self, type, value):
        if type == javaobj.JavaObjectConstants.TYPE_BYTE:
            return self.doc.createTextNode(hex(value))
        elif type == javaobj.JavaObjectConstants.TYPE_CHAR:
            return self.doc.createTextNode(str(value))
        elif type == javaobj.JavaObjectConstants.TYPE_DOUBLE:
            return self.doc.createTextNode(str(value))
        elif type == javaobj.JavaObjectConstants.TYPE_FLOAT:
            return self.doc.createTextNode(str(value))
        elif type == javaobj.JavaObjectConstants.TYPE_INTEGER:
            return self.doc.createTextNode(hex(value))
        elif type == javaobj.JavaObjectConstants.TYPE_LONG:
            return self.doc.createTextNode(hex(value))
        elif type == javaobj.JavaObjectConstants.TYPE_SHORT:
            return self.doc.createTextNode(hex(value))
        elif type == javaobj.JavaObjectConstants.TYPE_BOOLEAN:
            return self.doc.createTextNode('True' if value else 'False')


    def __remove_childs(self, el, drange=None):
        for num,child in zip(range(len(el.childNodes)), el.childNodes):
            if drange:
                if num >= drange.start and num < drange.stop:
                    pass




if __name__ == '__main__':
    import javaobj
    import sys

#    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.FATAL)

    obj = None
    if len(sys.argv) > 1:
        obj = javaobj.load_all(open(sys.argv[1], 'rb'))
    else:
        obj = javaobj.load(sys.stdin)

    marsh = XmlMarshaller()
    xml = marsh.marshall(obj)

    print xml


