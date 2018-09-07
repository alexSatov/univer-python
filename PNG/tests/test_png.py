import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from png import PngParser, PngInfo


class TestParser(unittest.TestCase):
    suite = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'suite')
    pictures_dir = os.path.join(os.path.pardir, 'pictures')

    def test_parse_only_png_files(self):
        with self.assertRaises(AttributeError):
            parser = PngParser(os.path.join(self.suite, 'png.txt'))
            parser.parse()

    def test_parse_only_correct_png_files(self):
        with self.assertRaises(AttributeError):
            parser = PngParser(os.path.join(self.suite, 'xcrn0g04.png'))
            parser.parse()

    def test_correct_header_parse(self):
        parser = PngParser(os.path.join(self.suite, 'basn0g01.png'))
        parser.parse()
        header_bytes = parser.chunks['IHDR']
        self.assertEqual(13, len(header_bytes))
        self.assertEqual(bytes, type(header_bytes))

    def test_set_info_from_header(self):
        png = PngInfo(os.path.join(self.suite, 'basn0g01.png'))
        self.assertTrue(png.chunks['IHDR'] is not None)
        self.assertEqual(png.info['Width'], 32)
        self.assertEqual(png.info['Height'], 32)
        self.assertEqual(png.info['Bit depth'], 1)
        self.assertEqual(png.info['Color type'], '0 (Grayscale)')
        self.assertEqual(png.info['Compression method'], '0 (Deflate/Inflate)')
        self.assertEqual(png.info['Filter method'], '0 (Adaptive)')
        self.assertEqual(png.info['Interlace method'], '0 (Noninterlaced)\n')

    def test_set_transparency_info(self):
        png = PngInfo(os.path.join(self.suite, 'tbbn2c16.png'))
        self.assertTrue(png.chunks['tRNS'] is not None)
        self.assertEqual('\n'
                         '    Red: 65535\n'
                         '    Green: 65535\n'
                         '    Blue: 65535\n', png.info['Transparency'])

    def test_set_gamma_info(self):
        png = PngInfo(os.path.join(self.suite, 'tbbn2c16.png'))
        self.assertTrue(png.chunks['gAMA'] is not None)
        self.assertEqual('1.0', png.info['Gamma'].strip())

    def test_set_chromaticities_info(self):
        png = PngInfo(os.path.join(self.suite, 'ccwn2c08.png'))
        self.assertTrue(png.parser.chunks['cHRM'] is not None)
        self.assertEqual(png.info['White point x'], '31270')
        self.assertEqual(png.info['White point y'], '32900')
        self.assertEqual(png.info['Red x'], '64000')
        self.assertEqual(png.info['Red y'], '33000')
        self.assertEqual(png.info['Green x'], '30000')
        self.assertEqual(png.info['Green y'], '60000')
        self.assertEqual(png.info['Blue x'], '15000')
        self.assertEqual(png.info['Blue y'], '6000\n')

    def test_set_rendering_intent_info(self):
        png = PngInfo(os.path.join(self.pictures_dir, 'Brandon.png'))
        self.assertTrue(png.parser.chunks['sRGB'] is not None)
        self.assertEqual('Perceptual\n', png.info['Rendering intent'])

    def test_set_iccp_profile_info(self):
        png = PngInfo(os.path.join(self.pictures_dir, 'eggs.png'))
        self.assertTrue(png.parser.chunks['iCCP'] is not None)
        profile = png.info['Embedded Profile'].split('\n')
        self.assertEqual(81, len(profile))

    def test_set_text_info(self):
        png = PngInfo(os.path.join(self.suite, 'ct1n0g04.png'))
        self.assertTrue(png.parser.chunks['tEXt'] != [])
        self.assertEqual('PngSuite', png.info['Title'].strip())

    def test_set_zip_text_info(self):
        png = PngInfo(os.path.join(self.suite, 'ctzn0g04.png'))
        self.assertTrue(png.parser.chunks['zTXt'] != [])
        self.assertEqual(png.info['Copyright'].strip(),
                         'Copyright Willem van Schaik, Singapore 1995-96')

    def test_set_international_text_info(self):
        png = PngInfo(os.path.join(self.suite, 'ctfn0g04.png'))
        self.assertTrue(png.parser.chunks['iTXt'] != [])
        self.assertEqual(png.info['Title'].strip(),
                         '(lang: None, keyword: fi)\n'
                         '    Otsikko\x00PngSuite')

    def test_set_background_color_info(self):
        png = PngInfo(os.path.join(self.suite, 'bggn4a16.png'))
        self.assertTrue(png.parser.chunks['bKGD'] is not None)
        self.assertEqual(png.info['Background color'].strip(),
                         'Gray: 43908')

    def test_set_pixel_dimensions_info(self):
        png = PngInfo(os.path.join(self.suite, 'cdhn2c08.png'))
        self.assertTrue(png.chunks['pHYs'] is not None)
        self.assertEqual(png.info['Pixels per unit, X axis'], 4)
        self.assertEqual(png.info['Pixels per unit, Y axis'], 1)
        self.assertEqual(png.info['Unit'], 'Unknown\n')

    def test_set_significant_bits_info(self):
        png = PngInfo(os.path.join(self.suite, 'cdhn2c08.png'))
        name = 'Number of significant bits'
        self.assertTrue(png.chunks['sBIT'] is not None)
        self.assertEqual('\n'
                         '    In red: 4\n'
                         '    In green: 4\n'
                         '    In blue: 4\n', png.info[name])

    def test_set_suggested_palette_info(self):
        png = PngInfo(os.path.join(self.suite, 'ps1n0g08.png'))
        self.assertTrue(png.chunks['sPLT'] is not None)
        entry = png.info['six-cube'].split('\n')[1]
        self.assertEqual('    [0] - R:0 G:0 B:0 A:255 Frequency:0', entry)

    def test_set_palette_histogram_info(self):
        png = PngInfo(os.path.join(self.suite, 'ch2n3p08.png'))
        self.assertTrue(png.chunks['hIST'] is not None)
        entry = png.info['Palette histogram'].split('\n')[1]
        self.assertEqual('    Approximate of using 0 color in palette: 4',
                         entry)

    def test_set_time_info(self):
        png = PngInfo(os.path.join(self.suite, 'cm0n0g04.png'))
        self.assertTrue(png.parser.chunks['tIME'] is not None)
        self.assertEqual(png.info['Last modification time'],
                         '2000-1-1 12:34:56\n')

if __name__ == '__main__':
    unittest.main()
