'''
Created on Apr 24, 2015

@author: madmaze
'''
import unittest
import pytesseract as pyt
import Image

class TestStringMethods(unittest.TestCase):

    def test_image_to_string_basic(self):
        im = Image.open("test.png")
        res = pyt.image_to_string(im)
        self.assertEqual(res, ('This is a lot of 12 point text to test the\n' + 
                               'ocr code and see if it works on all types\n' +
                               'of file format.\n\nThe quick brown dog jumped over the\n' +
                               'lazy fox. The quick brown dog jumped\n' +
                               'over the lazy fox. The quick brown dog\n' +
                               'jumped over the lazy fox. The quick\n' +
                               'brown dog jumped over the lazy fox.'))

    
if __name__ == '__main__':
    unittest.main()