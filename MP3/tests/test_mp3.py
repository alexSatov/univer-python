import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from mp3 import Mp3Info, Mp3Parser, int_from_bin, int_from_bytes, bin_from_int


class TestCastFunctions(unittest.TestCase):
    def test_int_from_bytes_when_empty(self):
        self.assertEqual(0, int_from_bytes(b''))

    def test_int_from_bytes_when_zero(self):
        self.assertEqual(0, int_from_bytes(b'\x00'))

    def test_int_from_bytes_when_byte(self):
        self.assertEqual(167, int_from_bytes(b'\xA7'))

    def test_int_from_bytes_when_bytes(self):
        self.assertEqual(353502, int_from_bytes(b'\x05\x64\xDE'))

    def test_int_from_bin_when_empty(self):
        self.assertEqual(0, int_from_bin(''))

    def test_int_from_bin_when_zero(self):
        self.assertEqual(0, int_from_bin('0'))

    def test_int_from_bin_when_bin_value(self):
        self.assertEqual(11, int_from_bin('001011'))

    def test_int_from_bin_when_not_bin_value(self):
        with self.assertRaises(ValueError):
            int_from_bin('0105')

    def test_bin_from_int_when_zero(self):
        self.assertEqual('00000000', bin_from_int(0))

    def test_bin_from_int_when_negative_int_value(self):
        self.assertEqual('-00000110', bin_from_int(-6))

    def test_bin_from_int_when_int_value(self):
        self.assertEqual('00001000', bin_from_int(8))

    def test_bin_from_int_when_double_value(self):
        with self.assertRaises(TypeError):
            bin_from_int(7.4)

    def test_bin_from_int_when_change_bits_count(self):
        self.assertEqual('10100', bin_from_int(20, 5))

    def test_bin_from_int_when_value_bigger_then_bits_count(self):
        self.assertEqual('10100', bin_from_int(20, 3))


class TestMp3Parsing(unittest.TestCase):
    suite = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'suite')

    def test_parser_works(self):
        parser = Mp3Parser()
        parser.parse(os.path.join(self.suite, 'Afrojack - Whatever.mp3'))

        self.assertTrue(parser.frame_info)
        self.assertTrue(parser.byte_info)
        self.assertTrue(parser.frames_count != 0)

    def test_info_filling(self):
        info = Mp3Info(os.path.join(self.suite, 'Afrojack - Whatever.mp3'))
        self.assertTrue(info.info)

    def test_parse_only_mp3_files(self):
        with self.assertRaises(AttributeError):
            Mp3Info(os.path.join(self.suite, 'suite/notmp3.txt'))

    def test_parse_when_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Mp3Info(os.path.join(self.suite, 'lol.mp3'))

    def test_parse_frame_info_first(self):
        filename = 'Afrojack feat. Steve Aoki & Miss Palmer - No Beef.mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual('MPEG-1', info.info['MPEG Version'])
        self.assertEqual('Layer 3', info.info['Layer Version'])
        self.assertEqual('1 (Protected by CRC)', info.info['Protection Bit'])
        self.assertEqual('128000 Kb/sec', info.info['Bitrate Index'])
        self.assertEqual('44100 Hz', info.info['Sampling Rate Index'])
        self.assertEqual('Joint stereo (Stereo)', info.info['Channel Mode'])
        self.assertEqual('Audio is not copyrighted',
                         info.info['Copyright Bit'])
        self.assertEqual('Original media', info.info['Original Bit'])
        self.assertEqual('None', info.info['Emphasis'])

    def test_parse_frame_info_second(self):
        filename = 'Alison Mosshart & Carla Azar - Tomorrow Never Knows.mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual('320000 Kb/sec', info.info['Bitrate Index'])
        self.assertEqual('Stereo', info.info['Channel Mode'])
        self.assertEqual('Audio is copyrighted', info.info['Copyright Bit'])

    def test_parse_id3v1_tag_first(self):
        filename = 'Afrojack - Whatever.mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual('ID3v1.0', info.info['ID3v1 Version'])
        self.assertEqual('Whatever', info.info['Title'].replace('\x00', ''))
        self.assertEqual('Afrojack', info.info['Artist'].replace('\x00', ''))
        self.assertEqual('www.NewJams.net',
                         info.info['Album'].replace('\x00', ''))
        self.assertEqual('2013', info.info['Year'])
        self.assertEqual('Electronic', info.info['Genre'].replace('\x00', ''))
        self.assertEqual('www.NewJams.net',
                         info.info['Comment'].replace('\x00', ''))

    def test_parse_id3v23_tag_second_first(self):
        filename = 'Afrojack - Whatever.mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual('ID3v2.3', info.info["ID3v2 Version"])
        self.assertEqual(b'\x00Whatever', info.info["TIT2"])
        self.assertEqual(b'\x00Afrojack', info.info["TPE1"])
        self.assertEqual(b'\x00www.NewJams.net', info.info["TALB"])
        self.assertEqual(b'\x002013', info.info["TYER"])
        self.assertEqual(b'\x00Electronic', info.info["TCON"])
        self.assertEqual(b'\x00eng\x00www.NewJams.net - New Music Everyday!',
                         info.info["COMM"])
        self.assertEqual(b'\x00www.NewJams.net', info.info["TCOM"])
        self.assertEqual(b'\x00\x00www.NewJams.net', info.info["WXXX"])
        self.assertEqual(b'\x00eng\x00www.NewJams.net - New Music Everyday!',
                         info.info["USLT"])
        self.assertEqual(b'\x00eng\x00www.NewJams.net - New Music Everyday!',
                         info.info["SYLT"])

    def test_parse_id3v23_tag_second_second(self):
        filename = 'Alison Mosshart & Carla Azar - Tomorrow Never Knows.mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual("ID3v2.3", info.info['ID3v2 Version'])
        self.assertEqual(b'\x006/9', info.info['TRCK'])
        self.assertEqual(b'\x00Tomorrow Never Knows', info.info['TIT2'])
        self.assertEqual(b'\x00', info.info['TPE2'])
        self.assertEqual(
            b'\x00Sucker Punch (Original Motion Picture Soundtrack)',
            info.info['TALB'])

    def test_parse_id3v23_tag_second_third(self):
        filename = 'Afrojack feat. Steve Aoki & Miss Palmer - No Beef.mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual('ID3v2.3', info.info['ID3v2 Version'])
        self.assertEqual(b'\x00No Beef (Vocal Mix)', info.info['TIT2'])
        self.assertEqual(b'\x00Afrojack feat. Steve Aoki & Miss Palmer',
                         info.info['TPE1'])

    def test_parse_id3v22_tag_second_first(self):
        filename = 'Afrojack – Air Guitar (Ultra Music Festival Anthem).mp3'
        info = Mp3Info(os.path.join(self.suite, filename))

        self.assertEqual('ID3v2.2', info.info['ID3v2 Version'])
        self.assertEqual(b'Afrojack\x00', info.info['TP1'])
        self.assertEqual(b'Various Artists\x00', info.info['TP2'])
        self.assertEqual(b'7/17\x00', info.info['TRK'])
        self.assertEqual(b'1/1\x00', info.info['TPA'])
        self.assertEqual(b'2013\x00', info.info['TYE'])
        self.assertEqual(b'Dance\x00', info.info['TCO'])
        self.assertEqual(b'1\x00', info.info['TCP'])
        self.assertEqual(b'iTunes 11.0.1\x00', info.info['TEN'])
        self.assertEqual(b'edm people\x00', info.info['TAL'])
        self.assertEqual(b'Air Guitar (Ultra Music Festival Anthem)\x00',
                         info.info['TT2'])


if __name__ == '__main__':
    unittest.main()
