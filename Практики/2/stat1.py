def make_stat(filename):
    with open(filename, encoding='windows-1251') as file:
        all_text = file.read().split('\n')
    info = {}
    stat = {}
    female_names = 'Анастасия, София, Алиса, Полина, Анна, Елена,' \
                   'Кристина, Юлия, Ева, Елизавета, Алена, Алёна,' \
                   'Наташа, Наталья, Ольга, Валентина, Любовь, Алла,' \
                   'Оксана, Лидия, Тамара, Светлана, Вероника,' \
                   'Дарья, Екатерина, Мария, Татьяна, Александра,' \
                   'Галина, Надежда, Эльвера, Лилия, Олеся, Валерия,' \
                   'Ксения, Ирина, Софья, Евгения, Марина, Евдокия,'
    for string in all_text:
        if '<h3>' in string:
            year = string[string.index('<h3>') + 4:string.index('</h3>')]
            info[year] = []
        if '<a href' in string:
            name = string[string.index('/>') + 3:string.index('</a>')]
            info[year].append(name)
    for year in info:
        stat[year] = {'Жен.': {}, 'Муж.': {}}
        for full_name in info[year]:
            name = full_name.split(' ')
            if name[1] + ',' in female_names:
                if stat[year]['Жен.'].__contains__(name[1]):
                    stat[year]['Жен.'][name[1]] += 1
                else:
                    stat[year]['Жен.'][name[1]] = 1
            else:
                if stat[year]['Муж.'].__contains__(name[1]):
                    stat[year]['Муж.'][name[1]] += 1
                else:
                    stat[year]['Муж.'][name[1]] = 1
    return stat


def extract_years(stat):
    years = []
    for year in stat:
        years.append(year)
    years.sort()
    return years


def extract_general(stat):
    all_names = {}
    for year in stat:
        for sex in stat[year]:
            for name in stat[year][sex]:
                if all_names.__contains__(name):
                    all_names[name] += stat[year][sex][name]
                else:
                    all_names[name] = stat[year][sex][name]
    names_list = []
    for name in all_names:
        names_list.append((name, all_names[name]))
    names_list.sort(key=lambda x: -x[1])
    return names_list


def extract_general_male(stat):
    all_names = {}
    for year in stat:
        for name in stat[year]['Муж.']:
            if all_names.__contains__(name):
                all_names[name] += stat[year]['Муж.'][name]
            else:
                all_names[name] = stat[year]['Муж.'][name]
    names_list = []
    for name in all_names:
        names_list.append((name, all_names[name]))
    names_list.sort(key=lambda x: -x[1])
    return names_list


def extract_general_female(stat):
    all_names = {}
    for year in stat:
        for name in stat[year]['Жен.']:
            if all_names.__contains__(name):
                all_names[name] += stat[year]['Жен.'][name]
            else:
                all_names[name] = stat[year]['Жен.'][name]
    names_list = []
    for name in all_names:
        names_list.append((name, all_names[name]))
    names_list.sort(key=lambda x: -x[1])
    return names_list


def extract_year(stat, year):
    all_names = {}
    for sex in stat[year]:
        for name in stat[year][sex]:
            if all_names.__contains__(name):
                all_names[name] += stat[year][sex][name]
            else:
                all_names[name] = stat[year][sex][name]
    names_list = []
    for name in all_names:
        names_list.append((name, all_names[name]))
    names_list.sort(key=lambda x: -x[1])
    return names_list


def extract_year_male(stat, year):
    all_names = {}
    for name in stat[year]['Муж.']:
        if all_names.__contains__(name):
            all_names[name] += stat[year]['Муж.'][name]
        else:
            all_names[name] = stat[year]['Муж.'][name]
    names_list = []
    for name in all_names:
        names_list.append((name, all_names[name]))
    names_list.sort(key=lambda x: -x[1])
    return names_list


def extract_year_female(stat, year):
    all_names = {}
    for name in stat[year]['Жен.']:
        if all_names.__contains__(name):
            all_names[name] += stat[year]['Жен.'][name]
        else:
            all_names[name] = stat[year]['Жен.'][name]
    names_list = []
    for name in all_names:
        names_list.append((name, all_names[name]))
    names_list.sort(key=lambda x: -x[1])
    return names_list


if __name__ == '__main__':
    pass

