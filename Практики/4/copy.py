import re


class Log:
    pattern = re.compile(r'(?P<ip>(\d+\.?){4}\d+).*?'
                         r'(?P<date>\d+/\w+/\d+).*?'
                         r'(?P<page>(GET|PUT|POST|HEAD|OPTIONS|DELETE)'
                         r' .*? HTTP)'
                         r'.*?(?P<user_agent>\" \".*?\") '
                         r'(?P<processing_time>\d*)')

    def __init__(self, log_line):
        self.log_line = log_line
        log_info = Log.log_parser(self, Log.pattern)
        self.ip = log_info['ip']
        self.date = log_info['date']
        self.page = log_info['page'].split(' ')[1]
        self.user_agent = log_info['user_agent'][3:-1]
        self.processing_time = log_info['processing_time']

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date_info):
        months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                  'May': '05', 'June': '06', 'July': '07', 'Aug': '08',
                  'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        date_data = date_info.split('/')
        self._date = '{0}-{1}-{2}'.format(date_data[2],
                                          months[date_data[1]],
                                          date_data[0])

    @property
    def processing_time(self):
        return self._processing_time

    @processing_time.setter
    def processing_time(self, time):
        if time == '':
            self._processing_time = 0
        else:
            self._processing_time = int(time)

    def log_parser(self, pattern):
        log = re.match(pattern, self.log_line)
        log_info = log.groupdict()
        return log_info


class Statistic:
    def __init__(self):
        self.m_a_c_b_d = {}
        self.fastest_page = ''
        self.slowest_page = ''
        self.slowest_average_page = ''
        self.most_active_client = ''
        self.most_active_client_by_day = ''
        self.most_popular_page = ''
        self.most_popular_browser = ''
        self.stat = {'fastest_page': {'min_time': 10000000000,
                                      'min_page': ''},
                     'slowest_page': {'max_time': 0,
                                      'max_page': ''},
                     'slowest_average_page': {},
                     'most_active_client': {'max_count': 0,
                                            'seeking_item': ''},
                     'most_active_client_by_day': {},
                     'most_popular_page': {'max_count': 0,
                                           'seeking_item': ''},
                     'most_popular_browser': {'max_count': 0,
                                              'seeking_item': ''}
                     }

    def update_fastest_page(self, log):
        if log.processing_time <= self.stat['fastest_page']['min_time']:
            self.stat['fastest_page']['min_time'] = log.processing_time
            self.stat['fastest_page']['min_page'] = log.page
        self.fastest_page = self.stat['fastest_page']['min_page']

    def update_slowest_page(self, log):
        if log.processing_time >= self.stat['slowest_page']['max_time']:
            self.stat['slowest_page']['max_time'] = log.processing_time
            self.stat['slowest_page']['max_page'] = log.page
        self.slowest_page = self.stat['slowest_page']['max_page']

    def update_slowest_average_page(self, log):
        statistic = self.stat['slowest_average_page']
        max_average_time = 0
        max_average_page = ''
        if not statistic.__contains__(log.page):
            statistic[log.page] = [1, log.processing_time]
        else:
            statistic[log.page][0] += 1
            statistic[log.page][1] += log.processing_time
        for page in statistic:
            average_time = statistic[page][1] / statistic[page][0]
            if average_time > max_average_time:
                max_average_time = average_time
                max_average_page = page
        self.slowest_average_page = max_average_page

    def update_most_active_client(self, log):
        statistic = self.stat['most_active_client']
        if not statistic.__contains__(log.ip):
            statistic[log.ip] = 1
            if statistic[log.ip] > statistic['max_count']:
                statistic['max_count'] = statistic[log.ip]
                statistic['max_client'] = log.ip
            if statistic[log.ip] == statistic['max_count']:
                statistic['max_client'] = min(log.ip, statistic['max_client'])
        else:
            statistic[log.ip] += 1
            if statistic[log.ip] > statistic['max_count']:
                statistic['max_count'] = statistic[log.ip]
                statistic['max_client'] = log.ip
            if statistic[log.ip] == statistic['max_count']:
                statistic['max_client'] = min(log.ip, statistic['max_client'])
        self.most_active_client = statistic['max_client']

    def update_most_active_client_by_day(self, log):
        statistic = self.stat['most_active_client_by_day']
        if not statistic.__contains__(log.date):
            statistic[log.date] = {'max_count': 0,
                                   'max_client': ''}
        if not statistic[log.date].__contains__(log.ip):
            statistic[log.date][log.ip] = 1
            if statistic[log.date][log.ip] > statistic[log.date]['max_count']:
                statistic[log.date]['max_count'] = statistic[log.date][log.ip]
                statistic[log.date]['max_client'] = log.ip
            if statistic[log.date][log.ip] == \
                    statistic[log.date]['max_count']:
                statistic[log.date]['max_client'] = min(
                    log.ip, statistic[log.date]['max_client']
                )
        else:
            statistic[log.date][log.ip] += 1
            if statistic[log.date][log.ip] > statistic[log.date]['max_count']:
                statistic[log.date]['max_count'] = statistic[log.date][log.ip]
                statistic[log.date]['max_client'] = log.ip
            if statistic[log.date][log.ip] == \
                    statistic[log.date]['max_count']:
                statistic[log.date]['max_client'] = min(
                    log.ip, statistic[log.date]['max_client']
                )
        self.m_a_c_b_d[log.date] = \
            statistic[log.date]['max_client']
        buff = ''
        for date in sorted(self.m_a_c_b_d):
            buff += '  {}: {} \n'.format(
                date, self.m_a_c_b_d[date]
            )
        self.most_active_client_by_day = buff

    def update_most_popular_page(self, log):
        statistic = self.stat['most_popular_page']
        if not statistic.__contains__(log.page):
            statistic[log.page] = 1
            if statistic[log.page] > statistic['max_count']:
                statistic['max_count'] = statistic[log.page]
                statistic['max_page'] = log.page
            if statistic[log.page] == statistic['max_count']:
                statistic['max_page'] = min(log.page, statistic['max_page'])
        else:
            statistic[log.page] += 1
            if statistic[log.page] > statistic['max_count']:
                statistic['max_count'] = statistic[log.page]
                statistic['max_page'] = log.page
            if statistic[log.page] == statistic['max_count']:
                statistic['max_page'] = min(log.page, statistic['max_page'])
        self.most_popular_page = statistic['max_page']

    def update_most_popular_browser(self, log):
        statistic = self.stat['most_popular_browser']
        if not statistic.__contains__(log.user_agent):
            statistic[log.user_agent] = 1
            if statistic[log.user_agent] > statistic['max_count']:
                statistic['max_count'] = statistic[log.user_agent]
                statistic['max_browser'] = log.user_agent
            if statistic[log.user_agent] == statistic['max_count']:
                statistic['max_browser'] = min(log.user_agent, statistic['max_browser'])
        else:
            statistic[log.user_agent] += 1
            if statistic[log.user_agent] > statistic['max_count']:
                statistic['max_count'] = statistic[log.user_agent]
                statistic['max_browser'] = log.user_agent
            if statistic[log.user_agent] == statistic['max_count']:
                statistic['max_browser'] = min(log.user_agent, statistic['max_browser'])
        self.most_popular_browser = statistic['max_browser']

    def count_stat(self, log, item_type):
        stat_type = 'most_active_' + item_type
        statistic = self.stat[stat_type]
        if item_type == 'client':
            log_item = log.ip
        if item_type == 'page':
            log_item = log.page
        if item_type == 'browser':
            log_item = log.user_agemt
        if not statistic.__contains__(log_item):
            statistic[log_item] = 1
            if statistic[log_item] > statistic['max_count']:
                statistic['max_count'] = statistic[log_item]
                statistic['seeking_item'] = log_item
            if statistic[log_item] == statistic['max_count']:
                statistic['seeking_item'] = min(log_item, statistic['seeking_item'])
        else:
            statistic[log_item] += 1
            if statistic[log_item] > statistic['max_count']:
                statistic['max_count'] = statistic[log_item]
                statistic['seeking_item'] = log_item
            if statistic[log_item] == statistic['max_count']:
                statistic['seeking_item'] = min(log_item, statistic['seeking_item'])
                return statistic['seeking_item']

    def __str__(self):
        return 'FastestPage: {} \n' \
               'MostActiveClient: {} \n' \
               'MostActiveClientByDay: \n' \
               '{}' \
               '\n' \
               'MostPopularBrowser: {} \n' \
               'MostPopularPage: {} \n' \
               'SlowestAveragePage: {} \n' \
               'SlowestPage: {}'.format(self.fastest_page,
                                        self.most_active_client,
                                        self.most_active_client_by_day,
                                        self.most_popular_browser,
                                        self.most_popular_page,
                                        self.slowest_average_page,
                                        self.slowest_page)


stat = Statistic()

with open('example_3.log') as file:
    for line in file:
        try:
            current_log = Log(line)
        except AttributeError:
            continue
        if current_log.processing_time != 0:
            stat.update_fastest_page(current_log)
            stat.update_slowest_page(current_log)
            stat.update_slowest_average_page(current_log)
        stat.update_most_popular_page(current_log)
        stat.update_most_popular_browser(current_log)
        stat.update_most_active_client(current_log)
        stat.update_most_active_client_by_day(current_log)

print(stat)
