filename = 'f_mash.log.txt'

with open(filename) as f:
    for i, line in enumerate(f):
        if i == 100:
            break
        print(i, line)

    i = iter(f)
    while 1:
        try:
            line = next(i)
        except StopIteration:
            break


class LogParser:
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename)
        self.iterator = iter(self.f)

    def read_line(self):
        try:
            line = next(self.iterator)
            self.line = line
            self.line_number += 1
        except StopIteration:
            return None

    def parse_line(self):
        if "'vote_sex': 'woman'" in self.line:
            self.stats.setdefault('vote_sex_woman', 0)
            self.stats['vote_sex_woman'] += 1
        if "'vote_sex': 'man'" in self.line:
            self.stats.setdefault('vote_sex_man', 0)
            self.stats['vote_sex_man'] += 1

    def print_stats(self):
        print(self.stats)