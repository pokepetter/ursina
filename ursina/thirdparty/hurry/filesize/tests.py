import unittest, doctest

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite('README.txt'),
            doctest.DocTestSuite('hurry.filesize.filesize'),
        ))
