from collections import OrderedDict
from info import speed, protection, copyright, original, emphasis, \
    tag_version, mpeg_version, layer_version, channel_mode, \
    sampling_rate_index, bitrate_index, genre


def int_from_bytes(bytes_line):
    return int.from_bytes(bytes_line, byteorder='big')


def int_from_bin(bin_number):
    return int(bin_number, 2) if bin_number != '' else 0


def bin_from_int(int_number, bits_count=8):
    negative = int_number < 0
    binary_str = bin(int_number)[3:] if negative else bin(int_number)[2:]
    zero_count = bits_count - len(binary_str)
    result = zero_count * '0' + binary_str
    if negative:
        result = '-' + result
    return result


class Mp3Parser:
    def __init__(self):
        self.byte_info = {}
        self.frame_info = {}
        self.frames_count = 0

    def clear(self):
        self.byte_info = {}
        self.frame_info = {}
        self.frames_count = 0

    def parse(self, filename):
        self.clear()

        if filename[-4:] != '.mp3':
            raise AttributeError("This is not mp3 file")

        try:
            with open(filename, 'rb') as file:
                data = file.read()
                tag_pos = data.find(b'TAG')
                id3_pos = data.find(b'ID3')
                if tag_pos != -1:
                    self.read_id3v1_tag(data, tag_pos)
                if id3_pos != -1:
                    self.read_id3v2_tag(data, id3_pos)

                search_index = 0
                while True:
                    frame_header_index = data.find(b'\xff\xfb', search_index)

                    if frame_header_index == -1:
                        break

                    search_index += self.read_frame(frame_header_index, data)
        except FileNotFoundError:
            raise FileNotFoundError("Incorrect filename")

    def read_id3v1_tag(self, data, index):
        if data[index + 3] != 45:  # 45 - ascii код символа '+'
            self.byte_info['id3v1'] = data[index + 3: index + 128]
        else:
            self.byte_info['id3v1+'] = data[index + 4:index + 227]

    def read_id3v2_tag(self, data, index):
        if data[index + 3] < 5:
            tags_length = self.get_id3v2_tag_length(data[index+6: index+10])
            self.byte_info['id3v2'] = data[index + 3:index + 10]
            self.byte_info['tags'] = data[index + 10: index + 10 + tags_length]

    @staticmethod
    def get_id3v2_tag_length(len_bytes):
        binary_number = ''
        for byte in len_bytes:
            binary = bin_from_int(byte)[1:]
            binary_number += binary
        return int(binary_number, 2)

    def read_frame(self, index, data):
        header = data[index:index + 4]
        bin_header = bin_from_int(int_from_bytes(header), 32)
        self.set_frame_info(bin_header)
        frame_length = self.get_frame_lenght()
        self.frames_count += 1 if frame_length != 0 else 0
        return 4 + frame_length

    def set_frame_info(self, header):
        cache = self.frame_info.copy()
        try:
            self.frame_info['Audio version ID'] = mpeg_version[header[11:13]]
            self.frame_info['Layer index'] = layer_version[header[13:15]]
            self.frame_info['Protection bit'] = header[15]

            mpeg = self.frame_info['Audio version ID']
            layer = self.frame_info['Layer index']
            key = '{} {}'.format(mpeg, layer)

            self.frame_info['Bitrate index'] = \
                bitrate_index[key][header[16:20]]

            self.frame_info['Sampling rate index'] = \
                sampling_rate_index[mpeg][header[20:22]]

            self.frame_info['Padding bit'] = int_from_bin(header[22])
            self.frame_info['Channel mode'] = channel_mode[header[24:26]]
            self.frame_info['Copyright bit'] = copyright[header[28]]
            self.frame_info['Original bit'] = original[header[29]]
            self.frame_info['Emphasis'] = emphasis[header[30:]]
        except KeyError:
            self.frame_info = cache

    def get_frame_lenght(self):
        if self.frame_info != {}:
            bitrate = self.frame_info['Bitrate index'] * 1000
            sample_rate = self.frame_info['Sampling rate index']
            padding = self.frame_info['Padding bit']
            return 144*bitrate//sample_rate + padding
        return 0


class Mp3Info:
    parser = Mp3Parser()

    def __init__(self, filename):
        self.info = OrderedDict()
        self.filename = filename
        self.parser.parse(filename)
        self.frame_info = self.parser.frame_info
        self.byte_info = self.parser.byte_info
        self.keyset = self.parser.byte_info.keys()
        self.set_info()

    def set_info(self):
        self.set_frame_info()
        self.set_header_info()

    def set_frame_info(self):
        self.info['MPEG Version'] = self.frame_info['Audio version ID']
        self.info['Layer Version'] = self.frame_info['Layer index']

        protection_bit = self.frame_info['Protection bit']
        self.info['Protection Bit'] = '{} ({})'.format(
            protection_bit, protection[protection_bit])

        self.info['Bitrate Index'] = '{} Kb/sec'.format(
            self.frame_info['Bitrate index'] * 1000)

        self.info['Sampling Rate Index'] = '{} Hz'.format(
            self.frame_info['Sampling rate index'])

        self.info['Channel Mode'] = self.frame_info['Channel mode']
        self.info['Copyright Bit'] = self.frame_info['Copyright bit']
        self.info['Original Bit'] = self.frame_info['Original bit']
        self.info['Emphasis'] = self.frame_info['Emphasis']

    def set_header_info(self):
        if 'id3v1' in self.keyset:
            self.set_id3v1_header_info(self.byte_info['id3v1'])
        if 'id3v1+' in self.keyset:
            self.set_ext_id3v1_header_info(self.byte_info['id3v1+'])
        if 'id3v2' in self.keyset:
            self.set_id3v2_header_info(self.byte_info['id3v2'])
            self.set_tags_info(self.byte_info['tags'])

    def set_id3v1_header_info(self, data):
        self.info['ID3v1 Version'] = 'ID3v1.0'
        self.info['Title'] = data[:30].decode('latin-1')
        self.info['Artist'] = data[30:60].decode('latin-1')
        self.info['Album'] = data[60:90].decode('latin-1')
        self.info['Year'] = data[90:94].decode('latin-1')
        self.info['Genre'] = genre[data[-1]] if data[-1] < 126 else 'Unknown'

        if data[:-3] == 0:
            self.info['ID3v1 Version'] = 'ID3v1.1'
            self.info['Comment'] = data[94:122].decode('latin-1')
            self.info['Track number'] = data[-2]
        else:
            self.info['Comment'] = data[94:124].decode('latin-1')

    def set_ext_id3v1_header_info(self, data):
        self.info['ID3v1 Version'] = 'ID3v1.1 (Extended)'
        self.info['Title'] = data[:60].decode('latin-1')
        self.info['Artist'] = data[60:120].decode('latin-1')
        self.info['Album'] = data[120:180].decode('latin-1')
        self.info['Speed'] = speed[data[180]]
        self.info['Genre'] = data[181:211].decode('latin-1')
        self.info['Start time'] = data[211:217].decode('latin-1')
        self.info['End time'] = data[217:223].decode('latin-1')

    def set_id3v2_header_info(self, data):
        version = data[0]
        self.info['ID3v2 Version'] = tag_version[version]

    def set_tags_info(self, data):
        i = 0
        data_len = len(data)
        while i < data_len - 1:
            try:
                if self.info['ID3v2 Version'] == 'ID3v2.2':
                    tag, tag_data = self.try_get_next_triple_tag(data, i)
                    i += 7 + len(tag_data)
                else:
                    tag, tag_data = self.try_get_next_quadruple_tag(data, i)
                    i += 10 + len(tag_data)
            except UnicodeDecodeError:
                return
            self.set_tag_info(tag, tag_data)

    def set_tag_info(self, tag, tag_data):
        if tag not in ('', 'PIC', 'APIC') and tag_data != b'':
            if tag in self.info.keys():
                self.info[tag] += tag_data
            else:
                self.info[tag] = tag_data

    @staticmethod
    def try_get_next_triple_tag(data, i):
        tag = data[i:i + 3].decode('ascii')
        size = int_from_bytes(data[i + 3:i + 6])
        tag_data = data[i + 7:i + 6 + size]
        return tag, tag_data

    @staticmethod
    def try_get_next_quadruple_tag(data, i):
        tag = data[i:i + 4].decode('ascii')
        size = int_from_bytes(data[i + 4:i + 8])
        tag_data = data[i + 10:i + 10 + size]
        i += 10 + size
        return tag, tag_data

    def __str__(self):
        result = ''
        for key, value in self.info.items():
            result += ' {}: {} \n'.format(key, value)
        return result
