import unittest
import javaobj
import logging

class TestJavaobj(unittest.TestCase):

    def setUp(self):
        import sys
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    def read_file(self, filename):
        with open(filename, 'rb') as file:
            return file.read()

    def test_0_rw(self):
        jobj = self.read_file("obj0.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)
        self.assertEqual(pobj, b'\x00C')
        jobj_ = javaobj.dumps(pobj)
        self.assertEqual(jobj, jobj_)

    def test_1(self):
        jobj = self.read_file("obj1.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)
        self.assertEqual(pobj, b'\x7f\xef\xff\xff\xff\xff\xff\xff')
        jobj_ = javaobj.dumps(pobj)
        self.assertEqual(jobj, jobj_)

    def test_2(self):
        jobj = self.read_file("obj2.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)
        self.assertEqual(pobj, b'HelloWorld')
        jobj_ = javaobj.dumps(pobj)
        self.assertEqual(jobj, jobj_)

    def test_3(self):
        jobj = self.read_file("obj3.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)
        self.assertEqual(pobj, chr(0).encode("utf8"))
        jobj_ = javaobj.dumps(pobj)
        self.assertEqual(jobj, jobj_)

    def test_4(self):
        jobj = self.read_file("obj4.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)
        self.assertEqual(pobj, b'\x7F')

        jobj_ = javaobj.dumps(pobj)
        self.assertEqual(jobj, jobj_)

    def test_5(self):
        jobj = self.read_file("obj5.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        self.assertEqual(pobj.aField1, 'Gabba')
        self.assertEqual(pobj.aField2, None)

        classdesc = pobj.get_class()
        self.assertTrue(classdesc)
        self.assertEqual(classdesc.serialVersionUID, 0x7F0941F5)
        self.assertEqual(classdesc.name, "OneTest$SerializableTestHelper")
        print(classdesc)
        print(classdesc.flags)
        print(classdesc.fields_names)
        print(classdesc.fields_types)
        self.assertEqual(len(classdesc.fields_names), 3)

#        jobj_ = javaobj.dumps(pobj)
#        self.assertEqual(jobj, jobj_)

    def test_6(self):
        jobj = self.read_file("obj6.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)
        self.assertEqual(pobj.name, 'java.lang.String')

#        jobj_ = javaobj.dumps(pobj)
#        self.assertEqual(jobj, jobj_)

    def test_7(self):
        jobj = self.read_file("obj7.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        classdesc = pobj.get_class()
        print(classdesc)
        print(classdesc.fields_names)
        print(classdesc.fields_types)

    def test_super(self):
        jobj = self.read_file("objSuper.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        classdesc = pobj.get_class()
        print(classdesc)
        print(classdesc.fields_names)
        print(classdesc.fields_types)

        print(pobj.childString)
        print(pobj.bool)
        print(pobj.integer)

    def test_arrays(self):
        jobj = self.read_file("objArrays.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        classdesc = pobj.get_class()
        print(classdesc)
        print(classdesc.fields_names)
        print(classdesc.fields_types)

#        public String[] stringArr = {"1", "2", "3"};
#        public int[] integerArr = {1,2,3};
#        public boolean[] boolArr = {true, false, true};
#        public TestConcrete[] concreteArr = {new TestConcrete(), new TestConcrete()};

        print(pobj.stringArr)
        print(pobj.integerArr)
        print(pobj.boolArr)
        print(pobj.concreteArr)

    def test_enums(self):
        jobj = self.read_file("objEnums.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        classdesc = pobj.get_class()
        print(classdesc)
        print(classdesc.fields_names)
        print(classdesc.fields_types)

    def test_exception(self):
        jobj = self.read_file("objException.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        classdesc = pobj.get_class()
        print(classdesc)
        print(classdesc.fields_names)
        print(classdesc.fields_types)

    def test_sun_example(self):
        marshaller = javaobj.JavaObjectUnmarshaller(open("sunExample.ser", "rb"))
        pobj = marshaller.readObject()

        self.assertEqual(pobj.value, 17)
        self.assertTrue(pobj.next)

        pobj = marshaller.readObject()

        self.assertEqual(pobj.value, 19)
        self.assertFalse(pobj.next)

    def test_collections(self):
        jobj = self.read_file("objCollections.ser")
        pobj = javaobj.loads(jobj)
        print(pobj)

        print("arrayList:", pobj.arrayList)
        self.assertTrue(isinstance(pobj.arrayList, list))
        print("hashMap:", pobj.hashMap)
        self.assertTrue(isinstance(pobj.hashMap, dict))
        print("linkedList:", pobj.linkedList)
        self.assertTrue(isinstance(pobj.linkedList, list)) # Fails

if __name__ == '__main__':
    unittest.main()
