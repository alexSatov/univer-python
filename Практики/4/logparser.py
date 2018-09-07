import re
import sys


class Log:
    def __init__(self, log_line, pattern):
        self.log_line = log_line

        log_info = Log.log_parser(self, pattern)

        months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                  'May': '05', 'June': '06', 'July': '07', 'Aug': '08',
                  'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        date_data = log_info['date'].split('/')
        self.date = '{0}-{1}-{2}'.format(date_data[2],
                                         months[date_data[1]],
                                         date_data[0])

        self.client = log_info['ip']
        self.page = log_info['page'].split(' ')[1]
        self.user_agent = log_info['user_agent'][3:-1]

        if log_info['processing_time'] == '':
            self.processing_time = 0
        else:
            self.processing_time = int(log_info['processing_time'])

    def log_parser(self, pattern):
        log = re.match(pattern, self.log_line)
        log_info = log.groupdict()
        return log_info

    def get_default_date(self):
        return self.log_line.split('[', ']')[1]


class Statistic:
    def __init__(self):
        self.m_a_c_b_d = {}
        self.time_result = {'f_p': '',
                            's_p': '',
                            's_a_p': ''}
        self.most_active_client = ''
        self.most_active_client_by_day = ''
        self.most_popular_page = ''
        self.most_popular_browser = ''
        self.stat = {'fastest_page': {'min_time': -1,
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
        if self.stat['fastest_page']['min_time'] < 0:
            self.stat['fastest_page']['min_time'] = log.processing_time
        if log.processing_time <= self.stat['fastest_page']['min_time']:
            self.stat['fastest_page']['min_time'] = log.processing_time
            self.stat['fastest_page']['min_page'] = log.page
        self.time_result['f_p'] = self.stat['fastest_page']['min_page']

    def update_slowest_page(self, log):
        if log.processing_time >= self.stat['slowest_page']['max_time']:
            self.stat['slowest_page']['max_time'] = log.processing_time
            self.stat['slowest_page']['max_page'] = log.page
        self.time_result['s_p'] = self.stat['slowest_page']['max_page']

    def get_slowest_average_page(self):
        statistic = self.stat['slowest_average_page']
        max_average_time = 0
        max_average_page = ''
        for page in statistic:
            average_time = statistic[page][1] / statistic[page][0]
            if average_time > max_average_time:
                max_average_time = average_time
                max_average_page = page
        self.time_result['s_a_p'] = max_average_page

    def update_slowest_average_page(self, log):
        statistic = self.stat['slowest_average_page']
        if not statistic.__contains__(log.page):
            statistic[log.page] = [1, log.processing_time]
        else:
            statistic[log.page][0] += 1
            statistic[log.page][1] += log.processing_time

    def update_most_active_client(self, log):
        self.count_stat(log, 'client')
        client = self.stat['most_active_client']['seeking_item']
        self.most_active_client = client

    def update_active_client_by_day(self, log):
        statistic = self.stat['most_active_client_by_day']
        if not statistic.__contains__(log.date):
            statistic[log.date] = {'max_count': 0,
                                   'seeking_item': ''}
        self.count_stat(log, 'client_by_day')
        self.m_a_c_b_d[log.date] = statistic[log.date]['seeking_item']
        buff = ''
        for date in sorted(self.m_a_c_b_d):
            buff += '  {}: {} \n'.format(
                date, self.m_a_c_b_d[date]
            )
        self.most_active_client_by_day = buff

    def update_most_popular_page(self, log):
        self.count_stat(log, 'page')
        page = self.stat['most_popular_page']['seeking_item']
        self.most_popular_page = page

    def update_most_popular_browser(self, log):
        self.count_stat(log, 'browser')
        browser = self.stat['most_popular_browser']['seeking_item']
        self.most_popular_browser = browser

    def count_stat(self, log, item_type):
        if item_type == 'client' or item_type == 'client_by_day':
            stat_type = 'most_active_' + item_type
        else:
            stat_type = 'most_popular_' + item_type
        if item_type == 'client_by_day':
            statistic = self.stat[stat_type][log.date]
        else:
            statistic = self.stat[stat_type]
        if item_type == 'client' or item_type == 'client_by_day':
            log_item = log.client
        if item_type == 'page':
            log_item = log.page
        if item_type == 'browser':
            log_item = log.user_agent
        if not statistic.__contains__(log_item):
            statistic[log_item] = 1
            self.lexicographically_smaller(statistic, log_item)
        else:
            statistic[log_item] += 1
            self.lexicographically_smaller(statistic, log_item)

    @staticmethod
    def lexicographically_smaller(statistic, log_item):
        if statistic[log_item] > statistic['max_count']:
            statistic['max_count'] = statistic[log_item]
            statistic['seeking_item'] = log_item
        if statistic[log_item] == statistic['max_count']:
            statistic['seeking_item'] = min(log_item,
                                            statistic['seeking_item'])

    def __str__(self):
        return 'FastestPage: {} \n' \
               'MostActiveClient: {} \n' \
               'MostActiveClientByDay: \n' \
               '{}' \
               '\n' \
               'MostPopularBrowser: {} \n' \
               'MostPopularPage: {} \n' \
               'SlowestAveragePage: {} \n' \
               'SlowestPage: {}'.format(self.time_result['f_p'],
                                        self.most_active_client,
                                        self.most_active_client_by_day,
                                        self.most_popular_browser,
                                        self.most_popular_page,
                                        self.time_result['s_a_p'],
                                        self.time_result['s_p'])


def main():
    stat = Statistic()
    pattern = re.compile(r'(?P<ip>(\d+\.?){4}\d+).*?'
                         r'(?P<date>\d+/\w+/\d+).*?'
                         r'(?P<page>(GET|PUT|POST|HEAD|OPTIONS|DELETE)'
                         r' .*? HTTP)'
                         r'.*?(?P<user_agent>\" \".*?\") '
                         r'(?P<processing_time>\d*)')
    file = sys.stdin
    for line in file:
        try:
            current_log = Log(line, pattern)
        except AttributeError:
            continue
        if current_log.processing_time != 0:
            stat.update_fastest_page(current_log)
            stat.update_slowest_page(current_log)
            stat.update_slowest_average_page(current_log)
        stat.update_most_popular_page(current_log)
        stat.update_most_popular_browser(current_log)
        stat.update_most_active_client(current_log)
        stat.update_active_client_by_day(current_log)
    stat.get_slowest_average_page()
    print(stat)


if __name__ == '__main__':
    main()
