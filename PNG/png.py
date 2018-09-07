from zlib import decompress
from collections import OrderedDict


def int_from_bytes(bytes_line):
    return int.from_bytes(bytes_line, byteorder='big')


class PngParser:
    signature = b'\x89PNG\r\n\x1a\n'

    def __init__(self, file_name):
        self.file_name = file_name
        self.check_name()
        self.chunks = OrderedDict()
        self.init_chunks()

    def check_name(self):
        if len(self.file_name) <= 4 or self.file_name[-4:] != '.png':
            raise AttributeError('This is not .png file')

    def parse(self):
        try:
            with open(self.file_name, 'rb') as file:
                self.check_on_png_signature(file.read(8))
                chunk_len = -1

                while chunk_len != 0:
                    chunk_len = int_from_bytes(file.read(4))
                    current_chunk = self.read_next_chunk(file, chunk_len)
                    if current_chunk == 'IEND':
                        self.chunks['IEND'] = True
                    file.read(4)

            self.check_on_required_chunks()
        except FileNotFoundError or PermissionError or FileExistsError:
            raise AttributeError('Incorrect image path')

    def read_next_chunk(self, file, chunk_len):
        name_in_bytes = file.read(4)
        current_chunk = name_in_bytes.decode('ascii')

        if not current_chunk.isalpha():
            file.read(chunk_len)
            return

        if current_chunk not in self.chunks.keys():
            self.chunks[current_chunk] = None
        if self.chunks[current_chunk] is None:
            self.chunks[current_chunk] = file.read(chunk_len)
        elif type(self.chunks[current_chunk]) == list:
            self.chunks[current_chunk].append(file.read(chunk_len))

        return current_chunk

    def init_chunks(self):
        # главные
        self.chunks['IHDR'] = None
        self.chunks['PLTE'] = None
        self.chunks['IEND'] = False
        self.chunks['IDAT'] = []

        # дополнительные
        self.chunks['tRNS'] = None

        self.chunks['gAMA'] = None
        self.chunks['cHRM'] = None
        self.chunks['sRGB'] = None
        self.chunks['iCCP'] = None

        self.chunks['tEXt'] = []
        self.chunks['zTXt'] = []
        self.chunks['iTXt'] = []

        self.chunks['bKGD'] = None
        self.chunks['pHYs'] = None
        self.chunks['sBIT'] = None
        self.chunks['sPLT'] = []
        self.chunks['hIST'] = None
        self.chunks['tIME'] = None

    def get_initialised_chunks_list(self):
        chunks = []
        for chunk in self.chunks:
            if self.chunks[chunk] != [] and self.chunks[chunk] is not None:
                chunks.append(chunk)
        return chunks

    def print_file_data(self):
        for chunk, data in self.chunks.items():
            print('{}: {}'.format(chunk, data))

    def check_on_png_signature(self, signature):
        if signature != self.signature:
            raise AttributeError('Incorrect PNG signature')

    def check_on_required_chunks(self):
        if self.chunks['IHDR'] is None:
            raise AttributeError('Incorrect IHDR chunk')
        if not self.chunks['IDAT']:
            raise AttributeError('Incorrect IDAT chunk')
        if not self.chunks['IEND']:
            raise AttributeError('Incorrect IEND chunk')


class PngInfo:
    color_type = {0: 'Grayscale', 2: 'RGB', 3: 'Palette',
                  4: 'Grayscale with alpha', 6: 'RGB with alpha'}
    rendering_intent = {0: 'Perceptual', 1: 'Relative colorimetric',
                        2: 'Saturation', 3: 'Absolute colorimetric'}
    interlace = {0: 'Noninterlaced', 1: 'Adam7 Interlace'}

    def __init__(self, file_name):
        self.parser = PngParser(file_name)
        self.parser.parse()
        self.file_name = file_name
        self.chunks = self.parser.chunks
        self.info = OrderedDict()
        self.info['Chunks'] = str(self.parser.get_initialised_chunks_list())
        self.chunk_processors = {'IHDR': self.set_header_info,
                                 'tRNS': self.set_transparency_info,
                                 'gAMA': self.set_gamma_info,
                                 'cHRM': self.set_chromaticities_info,
                                 'sRGB': self.set_rendering_intent_info,
                                 'iCCP': self.set_icc_profile_info,
                                 'tEXt': self.set_text_info,
                                 'zTXt': self.set_zip_text_info,
                                 'iTXt': self.set_international_text_info,
                                 'bKGD': self.set_background_color_info,
                                 'pHYs': self.set_pixel_dimensions_info,
                                 'sBIT': self.set_significant_bits_info,
                                 'sPLT': self.set_suggested_palette_info,
                                 'hIST': self.set_palette_histogram_info,
                                 'tIME': self.set_time_info}
        self.set_info()

    def set_info(self):
        for chunk in self.parser.chunks.keys():
            chunk_data = self.parser.chunks[chunk]
            if chunk in self.chunk_processors.keys():
                self.chunk_processors[chunk](chunk_data)
            elif chunk_data is not None and chunk_data != [] \
                    and chunk[0].islower():
                if type(chunk_data) != list:
                    self.info[chunk] = chunk_data.hex() + '\n'
                else:
                    self.info[chunk] = ''
                    for bytes_line in chunk_data:
                        self.info[chunk] += bytes_line.hex()
                    self.info[chunk] += '\n'

    def set_header_info(self, header):
        try:
            self.info['Width'] = int_from_bytes(header[:4])
            self.info['Height'] = int_from_bytes(header[4:8])
            self.info['Bit depth'] = header[8]
            self.info['Color type'] = '{} ({})'.\
                format(header[9], self.color_type[header[9]])
            self.info['Compression method'] = '{} (Deflate/Inflate)'.\
                format(header[10])
            self.info['Filter method'] = '{} (Adaptive)'.\
                format(header[11])
            self.info['Interlace method'] = '{} ({})\n'.\
                format(header[12], self.interlace[header[12]])

            if self.info['Bit depth'] not in (1, 2, 4, 8, 16):
                bd = self.info['Bit depth']
                raise AttributeError('Incorrect bit depth: {}'.format(bd))
        except KeyError:
            raise AttributeError('Incorrect IHDR chunk')

    def set_transparency_info(self, transparency):
        if transparency is not None:
            self.info['Transparency'] = '\n'
            header = self.parser.chunks['IHDR']
            color_type = header[9]

            if color_type == 3:
                index = 0
                for alpha in transparency:
                    entry = '    Alpha for palette index {}: {}\n'.format(
                        index, alpha)
                    self.info['Transparency'] += entry
                    index += 1

            if color_type == 0:
                self.info['Transparency'] += '    Gray: {}\n'.format(
                    int_from_bytes(transparency))

            if color_type == 2:
                self.info['Transparency'] += '    Red: {}\n'.format(
                    int_from_bytes(transparency[:2]))
                self.info['Transparency'] += '    Green: {}\n'.format(
                    int_from_bytes(transparency[2:4]))
                self.info['Transparency'] += '    Blue: {}\n'.format(
                    int_from_bytes(transparency[4:]))

    def set_gamma_info(self, gamma):
        if gamma is not None:
            self.info['Gamma'] = '{}\n'.format(int_from_bytes(gamma) / 100000)

    def set_chromaticities_info(self, chrm):
        if chrm is not None:
            self.info['White point x'] = str(int_from_bytes(chrm[:4]))
            self.info['White point y'] = str(int_from_bytes(chrm[4:8]))
            self.info['Red x'] = str(int_from_bytes(chrm[8:12]))
            self.info['Red y'] = str(int_from_bytes(chrm[12:16]))
            self.info['Green x'] = str(int_from_bytes(chrm[16:20]))
            self.info['Green y'] = str(int_from_bytes(chrm[20:24]))
            self.info['Blue x'] = str(int_from_bytes(chrm[24:28]))
            self.info['Blue y'] = '{}\n'.format(int_from_bytes(chrm[28:]))

    def set_rendering_intent_info(self, index):
        if index is not None:
            index = int_from_bytes(index)
            self.info['Rendering intent'] = self.rendering_intent[index] + '\n'

    def set_icc_profile_info(self, byte_line):
        if byte_line is not None:
            name, profile = byte_line.split(b'\x00\x00')
            name = name.decode('latin-1')
            profile = decompress(profile).decode('latin-1')
            self.info[name] = '\n    {}\n'.format(profile.replace('\n',
                                                                  '\n    '))

    def set_text_info(self, bytes_lines):
        for byte_line in bytes_lines:
            keyword, text = byte_line.split(b'\x00')
            keyword, text = keyword.decode('latin-1'), text.decode('latin-1')
            self.info[keyword] = '\n    {}\n'.format(text.replace('\n',
                                                                  '\n    '))

    def set_zip_text_info(self, bytes_lines):
        for byte_line in bytes_lines:
            keyword, text = byte_line.split(b'\x00\x00')
            keyword = keyword.decode('latin-1')
            text = decompress(text).decode('latin-1')
            self.info[keyword] = '\n    {}\n'.format(text.replace('\n',
                                                                  '\n    '))

    def set_international_text_info(self, bytes_lines):
        for byte_line in bytes_lines:
            null_sep = byte_line.index(b'\x00')
            keyword = byte_line[:null_sep]
            keyword = keyword.decode('latin-1')
            comp_flag = byte_line[null_sep + 1]

            byte_line = byte_line[null_sep + 2:]
            null_sep = byte_line.index(b'\x00')
            lang_tag = byte_line[:null_sep]
            lang_tag = lang_tag.decode('ascii') if lang_tag != b'' else None

            byte_line = byte_line[null_sep + 1:]
            null_sep = byte_line.index(b'\x00')
            tr_keyword = byte_line[:null_sep]
            tr_keyword = tr_keyword.decode('utf-8') \
                if tr_keyword != b'' else None

            text = byte_line[null_sep + 1:]
            if text != b'':
                if comp_flag == 1:
                    text = decompress(text)
                text = text.decode('utf-8')
            else:
                text = str(None)

            self.info[keyword] = '(lang: {}, keyword: {})\n    {}\n'.format(
                lang_tag, tr_keyword, text.replace('\n', '\n    '))

    def set_background_color_info(self, color):
        if color is not None:
            self.info['Background color'] = '\n'
            header = self.parser.chunks['IHDR']
            color_type = header[9]

            if color_type == 3:
                self.info['Background color'] += '    Index: {}\n'.format(
                    int_from_bytes(color))

            if color_type in (0, 4):
                self.info['Background color'] += '    Gray: {}\n'.format(
                    int_from_bytes(color))

            if color_type in (2, 6):
                self.info['Background color'] += '    Red: {}\n'.format(
                    int_from_bytes(color[:2]))
                self.info['Background color'] += '    Green: {}\n'.format(
                    int_from_bytes(color[2:4]))
                self.info['Background color'] += '    Blue: {}\n'.format(
                    int_from_bytes(color[4:]))

    def set_pixel_dimensions_info(self, phys):
        if phys is not None:
            self.info['Pixels per unit, X axis'] = int_from_bytes(phys[:4])
            self.info['Pixels per unit, Y axis'] = int_from_bytes(phys[4:8])
            self.info['Unit'] = 'Unknown\n' if phys[8] == 0 else "Meter\n"

    def set_significant_bits_info(self, bits):
        if bits is not None:
            title = 'Number of significant bits'
            self.info[title] = '\n'
            header = self.parser.chunks['IHDR']
            color_type = header[9]

            if color_type == 0:
                self.info[title] += '    In gray: {}\n'.format(bits[0])

            if color_type in (2, 3, 6):
                self.info[title] += '    In red: {}\n'.format(bits[0])
                self.info[title] += '    In green: {}\n'.format(bits[1])
                self.info[title] += '    In blue: {}\n'.format(bits[2])

            if color_type == 6:
                self.info[title] += '    In alpha: {}\n'.format(bits[3])

    def set_suggested_palette_info(self, palettes):
        for palette in palettes:
            null_sep = palette.index(b'\x00')
            name = palette[:null_sep].decode('latin-1')
            self.info[name] = '\n'
            depth = palette[null_sep + 1]
            data = palette[null_sep + 2:]
            is_byte = True if depth == 8 else False
            length = 6 if depth == 8 else 10
            i = 0
            while True:
                entry = data[length*i:length*(i+1)]
                if entry == b'':
                    break
                red = entry[0] if is_byte else int_from_bytes(entry[:2])
                green = entry[1] if is_byte else int_from_bytes(entry[2:4])
                blue = entry[2] if is_byte else int_from_bytes(entry[4:6])
                alpha = entry[3] if is_byte else int_from_bytes(entry[6:8])
                frequency = int_from_bytes(entry[4:]) if is_byte else \
                    int_from_bytes(entry[8:])
                self.info[name] += \
                    '    [{}] - R:{} G:{} B:{} A:{} Frequency:{}\n'\
                    .format(i, red, green, blue, alpha, frequency)
                i += 1

    def set_palette_histogram_info(self, hist):
        if hist is not None:
            entities_count = len(self.parser.chunks['PLTE']) // 3
            self.info['Palette histogram'] = '\n'
            for i in range(entities_count):
                self.info['Palette histogram'] += \
                    '    Approximate of using {} color in palette: {}\n'.\
                    format(i, int_from_bytes(hist[i*2:(i+1)*2]))

    def set_time_info(self, time):
        if time is not None:
            year = int_from_bytes(time[:2])
            month, day = time[2], time[3]
            hour, minute, second = time[4], time[5], time[6]
            self.info['Last modification time'] = '{}-{}-{} {}:{}:{}\n'.\
                format(year, month, day, hour, minute, second)

    def __str__(self):
        result = ''
        for key, value in self.info.items():
            result += ' {}: {} \n'.format(key, value)
        return result
