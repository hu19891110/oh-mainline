##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test interface declarations against ExtensionClass-like classes.

These tests are to make sure we do something sane in the presence of
classic ExtensionClass classes and instances.
"""
import doctest
import unittest

from zope.interface.tests import odd
from zope.interface import Interface, implements, classProvides
from zope.interface import directlyProvides, providedBy, directlyProvidedBy
from zope.interface import classImplements, classImplementsOnly, implementedBy

class I1(Interface): pass
class I2(Interface): pass
class I3(Interface): pass
class I31(I3): pass
class I4(Interface): pass
class I5(Interface): pass

class Odd(object): __metaclass__ = odd.MetaClass

class B(Odd): __implemented__ = I2


# TODO: We are going to need more magic to make classProvides work with odd
#       classes. This will work in the next iteration. For now, we'll use
#       a different mechanism.

# from zope.interface import classProvides

class A(Odd):
    pass
classImplements(A, I1)

class C(A, B):
    pass
classImplements(C, I31)


class Test(unittest.TestCase):

    def failUnless(self, expr): # silence deprecation warnings under py3
        return self.assertTrue(expr)

    def failIf(self, expr): # silence deprecation warnings under py3
        return self.assertFalse(expr)

    def test_ObjectSpecification(self):
        c = C()
        directlyProvides(c, I4)
        self.assertEqual([i.getName() for i in providedBy(c)],
                         ['I4', 'I31', 'I1', 'I2']
                         )
        self.assertEqual([i.getName() for i in providedBy(c).flattened()],
                         ['I4', 'I31', 'I3', 'I1', 'I2', 'Interface']
                         )
        self.failUnless(I1 in providedBy(c))
        self.failIf(I3 in providedBy(c))
        self.failUnless(providedBy(c).extends(I3))
        self.failUnless(providedBy(c).extends(I31))
        self.failIf(providedBy(c).extends(I5))

        class COnly(A, B):
            pass
        classImplementsOnly(COnly, I31)

        class D(COnly):
            pass
        classImplements(D, I5)

        classImplements(D, I5)

        c = D()
        directlyProvides(c, I4)
        self.assertEqual([i.getName() for i in providedBy(c)],
                         ['I4', 'I5', 'I31'])
        self.assertEqual([i.getName() for i in providedBy(c).flattened()],
                         ['I4', 'I5', 'I31', 'I3', 'Interface'])
        self.failIf(I1 in providedBy(c))
        self.failIf(I3 in providedBy(c))
        self.failUnless(providedBy(c).extends(I3))
        self.failIf(providedBy(c).extends(I1))
        self.failUnless(providedBy(c).extends(I31))
        self.failUnless(providedBy(c).extends(I5))

        class COnly(A, B): __implemented__ = I31
        class D(COnly):
            pass
        classImplements(D, I5)

        classImplements(D, I5)
        c = D()
        directlyProvides(c, I4)
        self.assertEqual([i.getName() for i in providedBy(c)],
                         ['I4', 'I5', 'I31'])
        self.assertEqual([i.getName() for i in providedBy(c).flattened()],
                         ['I4', 'I5', 'I31', 'I3', 'Interface'])
        self.failIf(I1 in providedBy(c))
        self.failIf(I3 in providedBy(c))
        self.failUnless(providedBy(c).extends(I3))
        self.failIf(providedBy(c).extends(I1))
        self.failUnless(providedBy(c).extends(I31))
        self.failUnless(providedBy(c).extends(I5))

    def test_classImplements(self):
        class A(Odd):
            implements(I3)

        class B(Odd):
            implements(I4)

        class C(A, B):
            pass
        classImplements(C, I1, I2)
        self.assertEqual([i.getName() for i in implementedBy(C)],
                         ['I1', 'I2', 'I3', 'I4'])
        classImplements(C, I5)
        self.assertEqual([i.getName() for i in implementedBy(C)],
                         ['I1', 'I2', 'I5', 'I3', 'I4'])

    def test_classImplementsOnly(self):
        class A(Odd):
            implements(I3)

        class B(Odd):
            implements(I4)

        class C(A, B):
            pass
        classImplementsOnly(C, I1, I2)
        self.assertEqual([i.__name__ for i in implementedBy(C)],
                         ['I1', 'I2'])


    def test_directlyProvides(self):
        class IA1(Interface): pass
        class IA2(Interface): pass
        class IB(Interface): pass
        class IC(Interface): pass
        class A(Odd):
            pass
        classImplements(A, IA1, IA2)

        class B(Odd):
            pass
        classImplements(B, IB)

        class C(A, B):
            pass
        classImplements(C, IC)


        ob = C()
        directlyProvides(ob, I1, I2)
        self.failUnless(I1 in providedBy(ob))
        self.failUnless(I2 in providedBy(ob))
        self.failUnless(IA1 in providedBy(ob))
        self.failUnless(IA2 in providedBy(ob))
        self.failUnless(IB in providedBy(ob))
        self.failUnless(IC in providedBy(ob))

        directlyProvides(ob, directlyProvidedBy(ob)-I2)
        self.failUnless(I1 in providedBy(ob))
        self.failIf(I2 in providedBy(ob))
        self.failIf(I2 in providedBy(ob))
        directlyProvides(ob, directlyProvidedBy(ob), I2)
        self.failUnless(I2 in providedBy(ob))

    def test_directlyProvides_fails_for_odd_class(self):
        self.assertRaises(TypeError, directlyProvides, C, I5)

    # see above
    def TODO_test_classProvides_fails_for_odd_class(self):
        try:
            class A(Odd):
                classProvides(I1)
        except TypeError:
            pass # Sucess
        self.failUnless(False,
                     "Shouldn't be able to use directlyProvides on odd class."
                     )

    def test_implementedBy(self):
        class I2(I1): pass

        class C1(Odd):
            pass
        classImplements(C1, I2)

        class C2(C1):
            pass
        classImplements(C2, I3)

        self.assertEqual([i.getName() for i in implementedBy(C2)],
                         ['I3', 'I2'])




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    suite.addTest(doctest.DocTestSuite(odd))
    return suite


if __name__ == '__main__':
    unittest.main()
