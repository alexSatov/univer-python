import sys
import argparse


class GameSettings:
    _default_board_size = 10
    _default_config = 'classic'
    _default_player1 = 'player'
    _default_player2 = 'player'
    _default_file_name = 'settings.txt'

    def __init__(self, file_name=_default_file_name):
        self.board_size = GameSettings._default_board_size
        self.config = GameSettings._default_config
        self.player1 = GameSettings._default_player1
        self.player2 = GameSettings._default_player2
        self.file_name = file_name
        self.set()

    def set(self):
        self.load()
        if len(sys.argv) > 1 and sys.argv[1][-3:] != '.py':
            args = self.get_args()

            if args.default:
                self.set_default()

            if args.settings:
                self.print()

            if args.config:
                import configuration
                configuration.create()

            self.set_board_size(args.size)
            self.set_config(args.configfile)
            self.set_player1(args.player1)
            self.set_player2(args.player2)

            self.save()

    def set_default(self):
        self.board_size = GameSettings._default_board_size
        self.config = GameSettings._default_config
        self.player1 = GameSettings._default_player1
        self.player2 = GameSettings._default_player2
        self.save()
        exit()

    def set_board_size(self, size):
        if type(size) is int:
            if 3 < size < 101 and size % 2 == 0:
                self.board_size = size
            else:
                print('Incorrect size')
                exit()

    def set_config(self, config):
        if type(config) is str:
            if config in ['classic', 'frisian'] or config[-4:] == '.txt':
                self.config = config
            else:
                print('Incorrect config name')
                exit()

    def set_player1(self, name):
        if type(name) is str:
            if name in ['player', 'bot', 'abot']:
                self.player1 = name
            else:
                print('Incorrect player name. Valid values: '
                      '\"player\", \"bot\" or \"abot\"')
                exit()

    def set_player2(self, name):
        if type(name) is str:
            if name in ['player', 'bot', 'abot']:
                self.player2 = name
            else:
                print('Incorrect player name. Valid values: '
                      '\"player\", \"bot\" or \"abot\"')
                exit()

    @staticmethod
    def get_args():
        info = 'Game \"Checkers\". Check README for detailed information'
        parser = argparse.ArgumentParser(description=info)

        parser.add_argument('-n', '--size', type=int,
                            help='set board size (3 < n < 101, '
                                 'n - even number)')

        parser.add_argument('-c', '--config', action='store_true',
                            help='launch board config, you must write fixed '
                                 'board size, after that create your own '
                                 'configuration of board (save to .txt file; '
                                 'use without other arguments)')

        parser.add_argument('-w', '--player1', type=str,
                            help='set player1 [player|bot|abot] '
                                 '(on white checkers)')

        parser.add_argument('-b', '--player2', type=str,
                            help='set player2 [player|bot|abot] '
                                 '(on black checkers)')

        parser.add_argument('-l', '--configfile', type=str,
                            help='load board config from .txt file (fixed '
                                 'size), default: \"classic\" or \"frisian\"')

        parser.add_argument('-s', '--settings', action='store_true',
                            help='print current settings '
                                 '(use without other arguments)')

        parser.add_argument('-d', '--default', action='store_true',
                            help='set default settings '
                                 '(if settings file is missing, '
                                 'creates this file with default settings; '
                                 'use without other arguments)')

        args = parser.parse_args()
        return args

    def save(self):
        with open(self.file_name, 'w') as file:
            file.write('board_size={}\n'.format(self.board_size))
            file.write('config={}\n'.format(self.config))
            file.write('player1={}\n'.format(self.player1))
            file.write('player2={}\n'.format(self.player2))

    def load(self):
        try:
            with open(self.file_name) as file:
                settings = {}
                for line in file:
                    line = line[:-1]
                    try:
                        key, value = line.split('=')
                    except ValueError:
                        continue
                    settings[key] = value
        except FileNotFoundError or FileExistsError:
            self.set_default()
            return

        self.board_size = int(settings['board_size'])
        self.config = settings['config']
        self.player1 = settings['player1']
        self.player2 = settings['player2']

    def print(self):
        try:
            with open(self.file_name) as file:
                for line in file:
                    print(line)
        except FileNotFoundError or FileExistsError:
            print('Settings file is not found. '
                  'Set default settings (-d)')
        exit()
