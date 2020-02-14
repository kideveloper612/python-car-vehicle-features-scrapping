import requests
import csv

from bs4 import BeautifulSoup
import os
import re


class Ford:
    def __init__(self):
        self.model_list = ['fusion', 'escape', 'edge', 'transit-connect', 'transit', 'taurus', 'ranger', 'mustang',
                           'fusion-hybrid', 'fusion-energi', 'focus-st', 'focus-electric', 'focus', 'flex', 'fiesta',
                           'f-550', 'f-450', 'f-350', 'f-250', 'f-150', 'explorer', 'expedition', 'ecosport', 'e-450',
                           'super-duty', 'mkx', 'gt', 'e-series', 'e-350', 'c-max-hybrid', 'c-max', 'c-max-energi',
                           'MKX-Black-Label', 'shelby-gt350-and-gt50r', 'mkx-black-label', 'fiesta-st', 'e-250',
                           'e-150', 'mustang-boss-302', 'f-series-super-duty', 'f-150-raptor', 'f-150-lariat',
                           'f-150-harley-davidson', 'mustang-svt', 'mustang-shelby-gt500', 'escape-hybrid', 'milan',
                           'mariner', 'mountaineer', 'explorer-sport-trac', 'taurus-x', 'sable', 'freestyle',
                           'five-hundred']
        self.valid_models = ['fusion', 'transit', 'taurus', 'mustang', 'focus', 'fiesta']
        self.valid_section_list = []
        self.csv_header = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'IMAGE']]

    def get_ford_models(self):
        path = './../fetch_videos_from_each_site/ford/output/Ford_how_to_video_Sorted.csv'
        with open(path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            model_list_from_file = []
            for row in csv_reader:
                if line_count < 1:
                    line_count += 1
                else:
                    print(line_count, row[2])
                    if not row[2] in model_list_from_file:
                        model_list_from_file.append(row[2])
                    line_count += 1
        print(model_list_from_file)

    def section_list(self, year, model):
        url = 'https://web.archive.org/web/%s0831231919/http://www.ford.com/cars/%s/features/' % (year, model)
        print(url)
        res_text = requests.get(url=url).text
        soup = BeautifulSoup(res_text, 'html.parser')
        try:
            nameplate = soup.select('div[id="nameplate-feature-nav"]')[0]
            category1 = nameplate.select('div[id="category#FeatureCategory1"]')[0].find_all('h3')[0].text
            category2 = nameplate.select('div[id="category#FeatureCategory2"]')[0].find_all('h3')[0].text
            category3 = nameplate.select('div[id="category#FeatureCategory3"]')[0].find_all('h3')[0].text
            category4 = nameplate.select('div[id="category#FeatureCategory4"]')[0].find_all('h3')[0].text
            return [category1, category2, category3, category4]
        except Exception as e:
            print(e)
            return None

    def widget_request(self, year, model, key):
        url = 'https://web.archive.org/web/%s0605020947/http://www.ford.com/cars/%s/features/FeatureCategory%s/' \
              '?widget=nameplate-features-content-area' % (year, model, key)
        res = requests.get(url=url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            nameplates = soup.select('div[id="nameplate-feature-tiles"]')[0]
            div_tags = nameplates.div.find_all(recursive=False)
            return div_tags
        else:
            return None

    def write_direct_csv(self, lines, filename):
        with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(lines)
        csv_file.close()

    def write_csv(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            self.write_direct_csv(lines=self.csv_header, filename=filename)
        self.write_direct_csv(lines=lines, filename=filename)

    def loop(self):
        for year in range(2010, 2018):
            for model in self.valid_models:
                sections = self.section_list(year=2013, model=model)
                print(sections)
                exit()
                if sections is not None:
                    for key, section in enumerate(sections, start=1):
                        utilities = self.widget_request(year, model, key)
                        if utilities is not None:
                            for utility in utilities:
                                if utility.has_attr('id'):
                                    continue
                                try:
                                    image = utility.select('img')[0]['src']
                                    if not 'https' in image:
                                        continue
                                    if not 'https://web.archive.org/' in image:
                                        image += 'https://web.archive.org' + image
                                    title = utility.select('h3')[0].text
                                    description = utility.select('p')[0].text
                                    print(year, 'FORD', model, section, title, description, image)
                                    self.write_csv(lines=[[year, 'FORD', model, section, title, description, image]],
                                                   filename='Ford_Features.csv')
                                except:
                                    continue


class Acura:
    def __init__(self):
        self.ford_class = Ford()
        self.buick_class = Buick()

    def get_2010(self, filename):
        models = ['RL', 'TL', 'TSX', 'ZDX', 'MDX', 'RDX']
        for model in models:
            feature_url = 'https://web.archive.org/web/20100117232755/http://www.acura.com/Features.aspx?model=%s&modelYear=2010' % model
            feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
            year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].text.split(' ')[0]
            uls = feature_soup.select('#content-wrap > div.content-body > ul > li > a')
            context_urls = []
            for ul in uls:
                context_url = 'https://web.archive.org' + ul['href'][:ul['href'].find('#')]
                if context_url in context_urls:
                    continue
                context_urls.append(context_url)
                result = re.search('&context=(.*)#', ul['href'])
                section = result.group(1).replace('+_+', ' ').strip()
                context_soup = BeautifulSoup(requests.get(url=context_url).text, 'html.parser')
                feature_group_tags = context_soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group > td > a')
                for feature_group_tag in feature_group_tags:
                    a_tag_id = feature_group_tag['href'].strip()
                    if len(a_tag_id) > 1:
                        search_key = {'id': a_tag_id.replace('#', '').strip() + 'X'}
                        dom_with_id = context_soup.find(**search_key)
                        span = dom_with_id.find('h5').find('span')
                        _ = span.extract()
                        title = dom_with_id.find('h5').get_text().strip()
                        try:
                            image = 'https://web.archive.org' + dom_with_id.find('img')['src']
                        except:
                            image = 'https://web.archive.org' + dom_with_id.find('img')['name']
                        description = dom_with_id.find('p').get_text()
                        line = [year, 'ACURA', model, section, title, description, image]
                        print(line)
                        ford_class = Ford()
                        ford_class.write_csv(lines=[line], filename=filename)

    def get_2011(self, filename):
        models = ['RL', 'TL', 'TSX', 'TSX Sport Wagon', 'ZDX', 'MDX', 'RDX']
        ford_class = Ford()

        def get_features(model):
            try:
                feature_url = 'https://web.archive.org/web/20110227042758/http://www.acura.com/Features.aspx?model=%s&modelYear=2011' % model
                feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
                year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                feature_url = 'https://web.archive.org/web/20110227042758/http://www.acura.com/Features.aspx?model=%s' % model
                feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
                year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            lis = feature_soup.select('#content-wrap > div.content-body > ul > li')
            for li in lis:
                section = li.find('h4').get_text()
                feature_group_url = 'https://web.archive.org/web/20110227065539/http://www.acura.com/Features.aspx?model=%s&modelYear=2011&context=%s' % (
                    model, section)
                soup = BeautifulSoup(requests.get(url=feature_group_url).text, 'html.parser')
                titles_dom = soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group')
                for title_dom in titles_dom:
                    title = title_dom.select('td.feature-name > a > span')[0].text.strip().replace('.', '').replace('-',
                                                                                                                    '').replace(
                        ',', '').replace('/', ' ')
                    search_id = '_'.join(str(x.lower()) for x in title.split(' ')).replace('&', '') + 'X'
                    search_key = {'id': search_id}
                    section_dom = soup.find(**search_key)
                    if section_dom.find('img').has_attr('src'):
                        img = 'https://web.archive.org' + section_dom.find('img')['src']
                    else:
                        img = 'https://web.archive.org' + section_dom.find('img')['name']
                    description = section_dom.find('p').get_text()
                    line = [year, 'ACURA', model, section, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        def get_accessories(model):
            try:
                accessory_url = 'https://web.archive.org/web/20110227042758/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2011' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                accessory_url = 'https://web.archive.org/web/20110227042758/http://www.acura.com/Accessories.aspx?model=%s' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            sections = accessory_soup.select(
                '#content-wrap > div.content-header > div.content-header-begin.has-packages-electronics > ul > li > a > span')
            for section in sections:
                if section.text == 'Overview':
                    continue
                sub_url = 'https://web.archive.org/web/20110227042758/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2011&context=%s' % (
                    model, section.text.lower())
                sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                accessory_lists = sub_soup.select('#accessories-%s > ul > li' % section.text.lower())
                for accessory_list in accessory_lists:
                    title = accessory_list.select('span > span.accessories-link > a')[0].get_text()
                    span_a = accessory_list.select('span > span.accessories-link > a')[0]
                    _ = span_a.extract()
                    description = accessory_list.select('span > span.accessories-link')[0].parent.find(text=True)
                    img = 'https://web.archive.org' + accessory_list.select('a > img')[0]['src']
                    line = [year, 'ACURA', model, section.text, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        for model in models:
            get_features(model=model)
            get_accessories(model)

    def get_2012(self, filename):
        models = ['RL', 'TL', 'TSX', 'TSX Sport Wagon', 'ZDX', 'MDX', 'RDX']
        ford_class = Ford()

        def get_features(model):
            feature_url = 'https://web.archive.org/web/20120114062637/http://www.acura.com/Features.aspx?model=%s&modelYear=2012' % model
            feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
            year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            lis = feature_soup.select('#content-wrap > div.content-body > ul > li')
            for li in lis:
                section = li.find('h4').get_text()
                feature_group_url = 'https://web.archive.org/web/20120114062637/http://www.acura.com/Features.aspx?model=%s&modelYear=2012&context=%s' % (
                    model, section)
                soup = BeautifulSoup(requests.get(url=feature_group_url).text, 'html.parser')
                titles_dom = soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group')
                for title_dom in titles_dom:
                    title = title_dom.select('td.feature-name > a > span')[0].text.strip().replace('.', '').replace('-',
                                                                                                                    '').replace(
                        ',', '').replace('/', ' ')
                    search_id = '_'.join(str(x.lower()) for x in title.split(' ')).replace('&', '') + 'X'
                    search_key = {'id': search_id}
                    section_dom = soup.find(**search_key)
                    if section_dom.find('img').has_attr('src'):
                        img = 'https://web.archive.org' + section_dom.find('img')['src']
                    else:
                        img = 'https://web.archive.org' + section_dom.find('img')['name']
                    description = section_dom.find('p').get_text()
                    line = [year, 'ACURA', model, section, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        def get_accessories(model):
            accessory_url = 'https://web.archive.org/web/20120227042758/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2012' % model
            accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
            year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            sections = accessory_soup.select(
                '#content-wrap > div.content-header > div.content-header-begin.has-packages-electronics > ul > li > a > span')
            for section in sections:
                if section.text == 'Overview':
                    continue
                sub_url = 'https://web.archive.org/web/20120227042758/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2012&context=%s' % (
                    model, section.text.lower())
                sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                accessory_lists = sub_soup.select('#accessories-%s > ul > li' % section.text.lower())
                for accessory_list in accessory_lists:
                    title = accessory_list.select('span > span.accessories-link > a')[0].get_text()
                    span_a = accessory_list.select('span > span.accessories-link > a')[0]
                    _ = span_a.extract()
                    description = accessory_list.select('span > span.accessories-link')[0].parent.find(text=True)
                    img = 'https://web.archive.org' + accessory_list.select('a > img')[0]['src']
                    line = [year, 'ACURA', model, section.text, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        for model in models:
            get_features(model=model)
            get_accessories(model)

    def get_2013(self, filename):
        models = ['TL', 'TSX', 'TSX Sport Wagon', 'ILX', 'ZDX', 'MDX', 'RDX']
        ford_class = Ford()

        def get_features(model):
            feature_url = 'https://web.archive.org/web/20130124121414/http://www.acura.com/Features.aspx?model=%s&modelYear=2013' % model
            feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
            year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            lis = feature_soup.select('#content-wrap > div.content-body > ul > li')
            for li in lis:
                section = li.find('h4').get_text()
                feature_group_url = 'https://web.archive.org/web/20130124121414/http://www.acura.com/Features.aspx?model=%s&modelYear=2013&context=%s' % (
                    model, section)
                soup = BeautifulSoup(requests.get(url=feature_group_url).text, 'html.parser')
                titles_dom = soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group')
                for title_dom in titles_dom:
                    title = title_dom.select('td.feature-name > a > span')[0].text.strip().replace('.', '').replace('-',
                                                                                                                    '').replace(
                        ',', '').replace('/', ' ').replace('(', '').replace(')', '').replace('™', '')
                    search_id = '_'.join(str(x.lower()) for x in title.split(' ')).replace('&', '') + 'X'
                    search_key = {'id': search_id}
                    section_dom = soup.find(**search_key)
                    if section_dom.find('img').has_attr('src'):
                        img = 'https://web.archive.org' + section_dom.find('img')['src']
                    else:
                        img = 'https://web.archive.org' + section_dom.find('img')['name']
                    description = section_dom.find('p').get_text()
                    line = [year, 'ACURA', model, section, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        def get_accessories(model):
            try:
                accessory_url = 'https://web.archive.org/web/20130124121414/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2013' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                accessory_url = 'https://web.archive.org/web/20130124121414/http://www.acura.com/Accessories.aspx?model=%s' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            sections = accessory_soup.select(
                '#content-wrap > div.content-header > div.content-header-begin.has-packages-electronics > ul > li > a > span')
            for section in sections:
                if section.text == 'Overview':
                    continue
                sub_url = 'https://web.archive.org/web/20130124121414/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2013&context=%s' % (
                    model, section.text.lower())
                sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                accessory_lists = sub_soup.select('#accessories-%s > ul > li' % section.text.lower())
                for accessory_list in accessory_lists:
                    title = accessory_list.select('span > span.accessories-link > a')[0].get_text()
                    span_a = accessory_list.select('span > span.accessories-link > a')[0]
                    _ = span_a.extract()
                    description = accessory_list.select('span > span.accessories-link')[0].parent.find(text=True)
                    if not 'https://web.archive.org' in accessory_list.select('a > img')[0]['src']:
                        img = 'https://web.archive.org' + accessory_list.select('a > img')[0]['src']
                    else:
                        img = accessory_list.select('a > img')[0]['src']
                    line = [year, 'ACURA', model, section.text, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        for model in models:
            get_features(model=model)
            get_accessories(model)

    def get_2014(self, filename):
        models = ['TL', 'TSX', 'TSX Sport Wagon', 'ILX', 'RLX', 'RDX', 'MDX']
        ford_class = Ford()

        def get_features(model):
            feature_url = 'https://web.archive.org/web/20140315203706/http://www.acura.com/Features.aspx?model=%s&modelYear=2014' % model
            feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
            year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            lis = feature_soup.select('#content-wrap > div.content-body > ul > li')
            for li in lis:
                section = li.find('h4').get_text()
                feature_group_url = 'https://web.archive.org/web/20140315203706/http://www.acura.com/Features.aspx?model=%s&modelYear=2014&context=%s' % (
                    model, section)
                soup = BeautifulSoup(requests.get(url=feature_group_url).text, 'html.parser')
                titles_dom = soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group')
                for title_dom in titles_dom:
                    title = title_dom.select('td.feature-name > a > span')[0].text.strip().replace('.', '').replace('-',
                                                                                                                    '').replace(
                        ',', '').replace('/', ' ').replace('(', '').replace(')', '').replace('TM', '')
                    search_id = '_'.join(str(x.lower()) for x in title.split(' ')).replace('&', '') + 'X'
                    search_key = {'id': search_id}
                    section_dom = soup.find(**search_key)
                    if section_dom.find('img').has_attr('src'):
                        img = 'https://web.archive.org' + section_dom.find('img')['src']
                    else:
                        img = 'https://web.archive.org' + section_dom.find('img')['name']
                    try:
                        description = section_dom.find('p').get_text()
                    except:
                        description = section_dom.find('ul').get_text()
                    line = [year, 'ACURA', model, section, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        def get_accessories(model):
            try:
                accessory_url = 'https://web.archive.org/web/20140315203706/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2014' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                accessory_url = 'https://web.archive.org/web/20140315203706/http://www.acura.com/Accessories.aspx?model=%s' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            sections = accessory_soup.select(
                '#content-wrap > div.content-header > div.content-header-begin.has-packages-electronics > ul > li > a > span')
            for section in sections:
                if section.text == 'Overview':
                    continue
                sub_url = 'https://web.archive.org/web/20140315203706/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2014&context=%s' % (
                    model, section.text.lower())
                sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                accessory_lists = sub_soup.select('#accessories-%s > ul > li' % section.text.lower())
                for accessory_list in accessory_lists:
                    title = accessory_list.select('span > span.accessories-link > a')[0].get_text()
                    span_a = accessory_list.select('span > span.accessories-link > a')[0]
                    _ = span_a.extract()
                    description = accessory_list.select('span > span.accessories-link')[0].parent.find(text=True)
                    if not 'https://web.archive.org' in accessory_list.select('a > img')[0]['src']:
                        img = 'https://web.archive.org' + accessory_list.select('a > img')[0]['src']
                    else:
                        img = accessory_list.select('a > img')[0]['src']
                    line = [year, 'ACURA', model, section.text, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        for model in models:
            get_features(model=model)
            get_accessories(model)

    def get_2015(self, filename):
        models = ['TLX', 'ILX', 'RLX', 'RDX', 'MDX']
        ford_class = Ford()

        def get_features(model):
            try:
                feature_url = 'https://web.archive.org/web/20150101010547/http://www.acura.com/Features.aspx?model=%s&modelYear=2015' % model
                feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
                year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                feature_url = 'https://web.archive.org/web/20150101010547/http://www.acura.com/Features.aspx?model=%s' % model
                feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
                year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            lis = feature_soup.select('#content-wrap > div.content-body > ul > li')
            for li in lis:
                section = li.find('h4').get_text()
                feature_group_url = 'https://web.archive.org/web/20150101010547/http://www.acura.com/Features.aspx?model=%s&modelYear=2015&context=%s' % (
                    model, section)
                soup = BeautifulSoup(requests.get(url=feature_group_url).text, 'html.parser')
                titles_dom = soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group')
                for title_dom in titles_dom:
                    title = title_dom.select('td.feature-name > a > span')[0].text.strip().replace('.', '').replace('-',
                                                                                                                    '').replace(
                        ',', '').replace('/', ' ').replace('(', '').replace(')', '').replace('TM', '')
                    search_id = '_'.join(str(x.lower()) for x in title.split(' ')).replace('&', '') + 'X'
                    search_key = {'id': search_id}
                    section_dom = soup.find(**search_key)
                    if section_dom.find('img').has_attr('src'):
                        img = 'https://web.archive.org' + section_dom.find('img')['src']
                    else:
                        img = 'https://web.archive.org' + section_dom.find('img')['name']
                    try:
                        description = section_dom.find('p').get_text()
                    except:
                        description = section_dom.find('ul').get_text()
                    line = [year, 'ACURA', model, section, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        def get_accessories(model):
            try:
                accessory_url = 'https://web.archive.org/web/20150101010547/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2015' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                accessory_url = 'https://web.archive.org/web/20150101010547/http://www.acura.com/Accessories.aspx?model=%s' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            sections = accessory_soup.select(
                '#content-wrap > div.content-header > div.content-header-begin.has-packages-electronics > ul > li > a > span')
            for section in sections:
                if section.text == 'Overview':
                    continue
                sub_url = 'https://web.archive.org/web/20150101010547/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2015&context=%s' % (
                    model, section.text.lower())
                sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                accessory_lists = sub_soup.select('#accessories-%s > ul > li' % section.text.lower())
                for accessory_list in accessory_lists:
                    title = accessory_list.select('span > span.accessories-link > a')[0].get_text()
                    span_a = accessory_list.select('span > span.accessories-link > a')[0]
                    _ = span_a.extract()
                    description = accessory_list.select('span > span.accessories-link')[0].parent.find(text=True)
                    if not 'https://web.archive.org' in accessory_list.select('a > img')[0]['src']:
                        img = 'https://web.archive.org' + accessory_list.select('a > img')[0]['src']
                    else:
                        img = accessory_list.select('a > img')[0]['src']
                    line = [year, 'ACURA', model, section.text, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        for model in models:
            get_features(model=model)
            get_accessories(model)

    def get_2016(self, filename):
        models = ['TLX', 'ILX', 'RLX', 'RDX', 'MDX']
        ford_class = Ford()

        def get_features(model):
            try:
                feature_url = 'https://web.archive.org/web/20160205221354/http://www.acura.com/Features.aspx?model=%s&modelYear=2016' % model
                feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
                year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                feature_url = 'https://web.archive.org/web/20160205221354/http://www.acura.com/Features.aspx?model=%s' % model
                feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
                year = feature_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            lis = feature_soup.select('#content-wrap > div.content-body > ul > li')
            for li in lis:
                section = li.find('h4').get_text()
                feature_group_url = 'https://web.archive.org/web/20160205221354/http://www.acura.com/Features.aspx?model=%s&modelYear=2016&context=%s' % (
                    model, section)
                soup = BeautifulSoup(requests.get(url=feature_group_url).text, 'html.parser')
                titles_dom = soup.select(
                    '#content-wrap > div.content-body > div.features-list > div > table > tbody > tr.feature-group')
                for title_dom in titles_dom:
                    title = title_dom.select('td.feature-name > a > span')[0].text.strip().replace('.', '').replace('-',
                                                                                                                    '').replace(
                        ',', '').replace('/', ' ').replace('(', '').replace(')', '').replace('TM', '').replace('®',
                                                                                                               'sup__sup')
                    search_id = '_'.join(str(x.lower()) for x in title.split(' ')).replace('&', '') + 'X'
                    search_key = {'id': search_id}
                    section_dom = soup.find(**search_key)
                    if section_dom.find('img'):
                        if section_dom.find('img').has_attr('src'):
                            img = 'https://web.archive.org' + section_dom.find('img')['src']
                        else:
                            img = 'https://web.archive.org' + section_dom.find('img')['name']
                    else:
                        img = ''
                    try:
                        description = section_dom.find('p').get_text()
                    except:
                        description = section_dom.find('ul').get_text()
                    line = [year, 'ACURA', model, section, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        def get_accessories(model):
            try:
                accessory_url = 'https://web.archive.org/web/20160205221354/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2016' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            except:
                accessory_url = 'https://web.archive.org/web/20160205221354/http://www.acura.com/Accessories.aspx?model=%s' % model
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).text, 'html.parser')
                year = accessory_soup.select('#sub-nav-begin > h2 > a > span')[0].get_text().split(' ')[0]
            sections = accessory_soup.select(
                '#content-wrap > div.content-header > div.content-header-begin.has-packages-electronics > ul > li > a > span')
            for section in sections:
                if section.text == 'Overview':
                    continue
                sub_url = 'https://web.archive.org/web/20160205221354/http://www.acura.com/Accessories.aspx?model=%s&modelYear=2016&context=%s' % (
                    model, section.text.lower())
                sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                accessory_lists = sub_soup.select('#accessories-%s > ul > li' % section.text.lower())
                for accessory_list in accessory_lists:
                    title = accessory_list.select('span > span.accessories-link > a')[0].get_text()
                    span_a = accessory_list.select('span > span.accessories-link > a')[0]
                    _ = span_a.extract()
                    description = accessory_list.select('span > span.accessories-link')[0].parent.find(text=True)
                    if not 'https://web.archive.org' in accessory_list.select('a > img')[0]['src']:
                        img = 'https://web.archive.org' + accessory_list.select('a > img')[0]['src']
                    else:
                        img = accessory_list.select('a > img')[0]['src']
                    line = [year, 'ACURA', model, section.text, title, description, img]
                    print(line)
                    ford_class.write_csv(lines=[line], filename=filename)

        for model in models:
            get_features(model=model)
            get_accessories(model)

    def get_2010_2016(self):
        self.get_2010(filename='Acura_2010_2016.csv')
        self.get_2011(filename='Acura_2010_2016.csv')
        self.get_2012(filename='Acura_2010_2016.csv')
        self.get_2013(filename='Acura_2010_2016.csv')
        self.get_2014(filename='Acura_2010_2016.csv')
        self.get_2015(filename='Acura_2010_2016.csv')
        self.get_2016(filename='Acura_2010_2016.csv')

    def read_acura(self):
        buick_class = Buick()
        lines = buick_class.read_csv('output/Acura/Acura_2010_2016.csv')
        for line in lines:

            if line[6] == 'IMAGE':
                continue
            if 'https://web.archive.org/images/' != line[6][:31]:
                new_image = line[6]
                inherit = line[6].split('http://www.acura.com/images/')[0] + 'http://www.acura.com/'
            else:
                new_image = inherit + line[6].split('https://web.archive.org/')[1]
            line[6] = new_image
            buick_class.write_csv(lines=[line], filename='Acura_2010_2016_again.csv')

    def get_2017(self):
        models = ['TLX', 'ILX', 'RLX', 'RDX', 'MDX', 'NSX']
        for model in models:
            feature_url = 'https://web.archive.org/web/20170624044026/http://www.acura.com/%s/features' % model.lower()
            feature_soup = BeautifulSoup(requests.get(url=feature_url).text, 'html.parser')
            sections = feature_soup.select('div.blade-wrapper > div > h6')
            print(feature_url)
            print(len(sections))
            for section in sections:
                section_parent = section.find_parent('section')

    def get_2018_rlx(self):
        url = 'https://web.archive.org/web/20171129075051/https://www.acura.com/RLX/features'
        soup = BeautifulSoup(requests.get(url=url).text, 'html.parser')
        sections = soup.select(
            'div.rzf-gry-title.text-x-small-left.text-small-left.text-medium-left.text-large-left.text-x-large-left')
        for section in sections:
            print(section.get_text().strip())

    def add_2017_2020(self):
        old_lines = self.buick_class.read_csv(file='output/Acura/Acura_2010_2016_again.csv', encode='true')
        self.buick_class.write_csv(filename='Acura_Features.csv', lines=old_lines)
        files = ['manual_2017.csv', 'manual_2018.csv', 'manual_2019.csv', 'manual_2020.csv']
        for file in files:
            file_path = 'output/%s' % file
            lines = self.buick_class.read_csv(file=file_path, encode='false')
            for line in lines:
                if file == 'manual_2020.csv':
                    line[6] = 'https://acura.com' + line[6]
                else:
                    line[6] = 'https://web.archive.org' + line[6]
                self.buick_class.write_csv(filename='Acura_Features.csv', lines=[line])


class Audi:
    def __init__(self):
        pass


class Buick:
    def __init__(self):
        self.csv_header = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'IMAGE']]

    def write_txt_url(self, lines, filename):
        with open(filename, "a") as my_file:
            for line in lines:
                my_file.write(line + '\n')

    def read_url(self):
        file = open('urls.txt', 'r')
        url_array = file.read().split('\n')
        return url_array[:-1]

    def write_direct_csv(self, lines, filename):
        with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(lines)
        csv_file.close()

    def write_csv(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            self.write_direct_csv(lines=self.csv_header, filename=filename)
        self.write_direct_csv(lines=lines, filename=filename)

    def read_csv(self, file, encode):
        records = []
        if encode == 'true':
            with open(file, "r", encoding='utf8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    print(row)
                    if line_count < 1:
                        line_count += 1
                        continue
                    count = 0
                    for x in row:
                        if len(x) > 1:
                            count += 1
                    if count == 7:
                        records.append(row)
            records.sort(key=lambda x: (x[0], x[2]))
            return records
        else:
            with open(file, "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    print(row)
                    if line_count < 1:
                        line_count += 1
                        continue
                    count = 0
                    for x in row:
                        if len(x) > 1:
                            count += 1
                    if count == 7:
                        records.append(row)
            records.sort(key=lambda x: (x[0], x[2]))
            return records

    def vehicle_tab(self, year):
        url = 'https://web.archive.org/web/%s1109064802/http://www.buick.com/' % year
        response = requests.get(url=url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            mds = soup.select('div[id="mds-cmp-1stlevelnavigation"]')[0]
            ul = mds.select('ul>li:first-child>ul>li.ext')
            return ul

    def get_request_urls(self):
        for year in range(2011, 2021):
            navigation = self.vehicle_tab(year=year)
            lines = []
            for model_soup in navigation:
                model = model_soup.find('a').text
                href = 'https://web.archive.org%s' % model_soup.find('a')['href'].strip()
                lines.append(href)
            self.write_txt_url(lines=lines)
        read_lines = self.read_url()
        for url in read_lines:
            for url_year in range(2011, 2021):
                request_url = (url[:-len(url.split('/')[-1])] + '%s-' + url.split('/')[-1]) % url_year
                print(request_url)
                if requests.get(url=request_url).status_code == 200:
                    print("=================", request_url, "=========================")
                    self.write_txt_url([request_url])

    def get_year(self, url):
        try:
            individual_soup = BeautifulSoup(requests.get(url=url).text, 'html.parser')
            navigation = individual_soup.select('div[id="mds-cmp-2ndlevelnavigation"]>dl>dt>a>span')[0].text
            year = navigation[0:4].strip()
            model = navigation[4:].strip()
            return year, model
        except:
            return None

    def get_year_again(self, url):
        try:
            soup = BeautifulSoup(requests.get(url=url).text, 'html.parser')
            wrapper = soup.select('#mhc1 .mh_content_wrapper .mh_title_1 span>span')
            year = wrapper[0].text.strip()
            model = wrapper[1].text.strip()
            return year, model
        except:
            return None

    def get_section(self, url):
        soup = BeautifulSoup(requests.get(url=url).text, 'html.parser')
        this_page = soup.find(text=re.compile(r'ON THIS PAGE')).parent
        if this_page.name == 'span':
            h2 = this_page.parent.findNext('h2')
            span = h2.find('span').text
            return span
        # return this_page

    def tag_visible(element):
        from bs4.element import Comment
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def from_2014(self):
        for year in range(2014, 2018):
            url = 'https://web.archive.org/web/%s0228093211/http://www.buick.com/' % year
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            area_footer = soup.select('#mds-area-footer')[0] \
                .find('div', {'class': 'mds-area-pf6 nav_footer_1 mod modNav_footer_1'}) \
                .find('div', {'class': 'mds-cmp-navigation06 nav_sitemap_2 mod modNav_sitemap_2'}) \
                .find('ul').select('li>a')
            for area in area_footer:
                area_array = area.text.split(' ')
                if len(area_array) == 2:
                    model = area_array[1]
                else:
                    model = area.text
                sub_url = 'https://web.archive.org%s' % area['href']
                if year == 2014:
                    sub_soup = BeautifulSoup(
                        requests.get(url=sub_url).text.replace('<figure>', '').replace('</figure>', ''), 'html.parser')
                else:
                    sub_soup = BeautifulSoup(requests.get(url=sub_url).text, 'html.parser')
                wells = sub_soup.find_all('div', {'class': 'cnt_well_c2 section'})
                for well in wells:
                    lis = well.select('ul li')
                    for li in lis:
                        if li.h2:
                            section = li.h2.text.split('/')[0].strip()
                            if len(li.h2.text.split('/')) > 1:
                                title = li.h2.text.split('/')[1].strip()
                            else:
                                title = ''
                            if section.lower() == 'tools':
                                continue
                        description_element = li.find('div', {'class': 'caption txtWrp'})
                        description = description_element.getText().strip() if description_element else ""
                        image_element = li.find('div', {'class': 'fs-content'})
                        initial_image = image_element.find('img')['src'] if image_element else ''
                        if initial_image != '' and initial_image[-4:] != '.jpg':
                            initial_image = image_element.find('img')['data-orig-src']
                        image = 'https://web.archive.org%s' % initial_image
                        if len(image) < len('https://web.archive.org') + 2:
                            continue
                        self.write_csv(lines=[[str(year), 'Buick', model, section, title, description, image]],
                                       filename='2011_2017.csv')
                        print(year, model, section, title, description, image)

    def add_2011_2017(self):
        f_lines = self.read_csv()
        self.write_csv(lines=f_lines, filename='2011_2017.csv')
        self.from_2014()

    def get_2018(self):
        initial_url = 'https://web.archive.org/web/20180329164311/http://www.buick.com/navigation/primary-nav-link/vehicles.html'
        soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
        colums = soup.find_all('div', {'class': 'q-margin-base q-mod q-vehicle-tile'})
        for colum in colums:
            link = 'https://web.archive.org' + colum.find('a')['href']
            if 'previous-year' in link:
                continue
            print(link)

    def lines_manual_file(self):
        lines_11_17 = self.read_csv(file='output/2011_2017.csv')
        self.write_csv(filename='2011_2018.csv', lines=lines_11_17)
        lines_18 = self.read_csv(file='output/2018_manual.csv')
        for line_18 in lines_18:
            new_line = [line_18[0], line_18[1], line_18[2], line_18[3], line_18[4], line_18[5], 'https://web.archive'
                                                                                                '.org' + line_18[6]]
            self.write_csv(filename='2011_2018.csv', lines=[new_line])

    def read_write(self):
        lines = self.read_csv()
        self.write_csv(lines=lines, filename='2011_2013.csv')

    def from_2019(self):
        links_19 = ['https://buick.com/suvs/previous-year/encore', 'https://buick.com/suvs/previous-year/envision',
                    'https://buick.com/suvs/previous-year/enclave',
                    'https://buick.com/crossovers/previous-year/regal/tourx',
                    'https://buick.com/sedans/previous-year/regal/sportback',
                    'https://buick.com/sedans/previous-year/regal/gs',
                    'https://buick.com/sedans/previous-year/lacrosse-full-size-luxury-sedan',
                    'https://buick.com/suvs/previous-year/enclave/avenir',
                    'https://buick.com/sedans/previous-year/regal/avenir',
                    'https://buick.com/sedans/previous-year/lacrosse-avenir-full-size-luxury-sedan']
        links_20 = ['https://buick.com/suvs/encore', 'https://buick.com/suvs/envision',
                    'https://buick.com/suvs/enclave', 'https://buick.com/crossovers/regal/tourx',
                    'https://buick.com/sedans/regal/sportback', 'https://buick.com/sedans/regal/gs',
                    'https://buick.com/sedans/lacrosse-full-size-luxury-sedan', 'https://buick.com/suvs/enclave/avenir',
                    'https://buick.com/sedans/regal/avenir',
                    'https://buick.com/sedans/lacrosse-avenir-full-size-luxury-sedan']

        for link in links_19:
            print(link)
        for link_19 in links_19:
            soup = BeautifulSoup(requests.get(url=link_19).text, 'html.parser')
            display = soup.find('h1', {'class': 'q-display1'}).get_text().strip()
            if 'PAGE NOT FOUND' in display:
                continue
            model = display[4:].strip()
            if model == 'L AVENIR':
                model = display.strip()
            features = soup.find('span', string="Features")
            if features:
                parent = 'https://buick.com' + features.parent['href']
                sections = BeautifulSoup(requests.get(url=parent).text, 'html.parser').select(
                    'ul.no-bullet.inline-list.q-js-tirtiary-list-items.q-list-layout>li>a')
                for section in sections:
                    section_name = section.find('span').getText().strip()
                    section_link = 'https://buick.com' + section['href']
                    # feature_soup = BeautifulSoup(requests.get(url=section_link).text, 'html.parser')
                    # grid = feature_soup.select('div.row.q-gridbuilder .grid-column-alignment-left.columns .medium-margin')
                    print(link_19, section_name, section_link)

    def add_19_20(self):
        lines_19 = self.read_csv(file='output/2019_manual.csv')
        lines_20 = self.read_csv(file='output/2020_manual.csv')
        lines = []
        for line in lines_19:
            line[6] = 'https://www.buick.com' + line[6]
            lines.append(line)
        for line in lines_20:
            line[6] = 'https://www.buick.com' + line[6]
            lines.append(line)
        lines_before = self.read_csv(file='output/2011_2018.csv')
        for line in lines_before:
            lines.append(line)
        lines.sort(key=lambda x: (x[0], x[2], x[3]))
        self.write_csv(lines=lines, filename='Buick_Features.csv')


class Toyota:
    def __init__(self):
        self.buick_class = Buick()

    def get_2010_2012(self):
        for year_loop in range(2010, 2011):
            url = 'http://web.archive.org/web/%s0411061440/http://www.toyota.com/' % year_loop
            models = BeautifulSoup(requests.get(url=url).text, 'html.parser').select('#globalnav-container .model-name')
            tmp_thumbnail_url_list = []
            total_lines = []
            for model in models:
                model_name = model.get_text().strip()
                thumbnail_url = 'http://web.archive.org/web/%s0411061440/http://www.toyota.com/%s/accessories.html' % (
                    year_loop, model_name.replace(
                        ' ', '').lower().replace('hybrid', ''))
                if thumbnail_url in tmp_thumbnail_url_list:
                    continue
                tmp_thumbnail_url_list.append(thumbnail_url)
                print(thumbnail_url)
                year_soup = BeautifulSoup(requests.get(url=thumbnail_url.replace('/accessories.html', '')).text,
                                          'html.parser').title.get_text().split(' ')
                for word in year_soup:
                    try:
                        year = int(word)
                    except:
                        continue
                thumbnail_soup = BeautifulSoup(requests.get(url=thumbnail_url).text, 'html.parser')
                photo_galleries = thumbnail_soup.select('.photoGallery')
                for photo_gallery in photo_galleries:
                    section = photo_gallery.find('div', {'class': 'gallery-heading-text'}).get_text()
                    thumb_collection = photo_gallery.select('.thumbcollection .thumbnail')

                    for thumb in thumb_collection:
                        title = thumb.get_text().strip()
                        image = 'https://web.archive.org' + thumb.select('a > img')[0]['src']
                        description_url = 'https://web.archive.org' + thumb.find_all('a', recursive=False)[0]['href']
                        description_soup = BeautifulSoup(requests.get(url=description_url).text, 'html.parser')
                        try:
                            description = \
                                description_soup.select('#overlayDiv > div.model-layer-box-content > div.descrip-text')[
                                    0].getText()
                        except:
                            continue
                        line = [year, 'Toyota', model_name, section, title, description, image]
                        if not line in total_lines:
                            print(line)
                            self.buick_class.write_csv(lines=[line], filename='toyota_2010_2012.csv')
                            total_lines.append(line)

    def get_2013_2015(self):
        model_json_url = 'http://web.archive.org/web/20140511154040/http://www.toyota.com/ToyotaSite/rest/lscs/getDocument?templatePath=templatedata/TComVehiclesData/Series/data/CombinedSeries.xml'
        model_json = requests.get(url=model_json_url).json()['Root']['Series']
        lines = []
        for mode in model_json:
            if mode['modelYear'] == 2013 or 2014:
                model_name = mode['modelName']
                if '-' in model_name:
                    section_url = 'http://web.archive.org/web/%s1002093710/http://www.toyota.com/%s' % (
                        mode['modelYear'], model_name.replace(
                            ' ', '-').lower())
                else:
                    section_url = 'http://web.archive.org/web/%s1002093710/http://www.toyota.com/%s' % (
                        mode['modelYear'], model_name.replace(
                            ' ', '').lower().replace('hybrid', ''))
                section_soup = BeautifulSoup(requests.get(url=section_url).text, 'html.parser')
                mlp_features = section_soup.select('.content-section.panel-container')
                for mlp_feature in mlp_features:
                    if len(mlp_feature.select('.page-header > h2')) > 0:
                        section = mlp_feature.select('.page-header > h2')[0].get_text()
                    elif len(mlp_feature.select('.page-header > h3')) > 0:
                        section = mlp_feature.select('.page-header > h3')[0].get_text()
                    contents = mlp_feature.select('.page-content .tab-content .tab-pane')
                    for content in contents:
                        try:
                            image = 'https://web.archive.org' + content.find('img')['src']
                        except:
                            continue
                        if content.find('h3'):
                            title_dom = content.find('h3')
                            description = title_dom.find_next('p').getText().strip()
                        elif content.find('h4'):
                            title_dom = content.find('h4')
                            description = title_dom.find_next('p').getText().strip()
                        elif content.find('h5'):
                            title_dom = content.find('h5')
                            description = title_dom.find_next('p').getText().strip()
                        else:
                            continue
                        title = title_dom.getText().strip()
                        line = [mode['modelYear'], 'Toyota', model_name, section, title, description, image]
                        lines.append(line)
                        print(line)
                print(section_url)
        lines.sort(key=lambda x: (x[0], x[2]))
        print(lines)
        self.buick_class.write_csv(lines=lines, filename='toyota_2013_2014.csv')

    def get_2015_2016(self):
        model_json_url = 'http://web.archive.org/web/20160511154040/http://www.toyota.com/ToyotaSite/rest/lscs/getDocument?templatePath=templatedata/TComVehiclesData/Series/data/CombinedSeries.xml'
        model_json = requests.get(url=model_json_url).json()['Root']['Series']
        model_list = []
        for model in model_json:
            if not model['modelName'] in model_list:
                model_list.append(model['modelName'])
        lines = []
        for mode in model_json:
            if mode['modelYear'] == 2015 or 2016:
                model_name = mode['modelName']
                if '-' in model_name:
                    section_url = 'http://web.archive.org/web/%s1002093710/http://www.toyota.com/%s' % (
                        mode['modelYear'], model_name.replace(
                            ' ', '-').lower())
                else:
                    section_url = 'http://web.archive.org/web/%s1002093710/http://www.toyota.com/%s' % (
                        mode['modelYear'], model_name.replace(
                            ' ', '').lower().replace('hybrid', ''))
                section_soup = BeautifulSoup(requests.get(url=section_url).text, 'html.parser')
                mlp_features = section_soup.select('.mlp-features-section')
                for mlp_feature in mlp_features:
                    if len(mlp_feature.select('.mlp-features-header > h2')) > 0:
                        section = mlp_feature.select('.mlp-features-header .mlp-features-title')[0].get_text()
                    contents = mlp_feature.select('.mlp-features-content .mlp-feature .mlp-feature-body')
                    for content in contents:
                        if not content.select('.mlp-feature-image img'):
                            continue
                        img_soup = content.select('.mlp-feature-image img')[0]
                        if img_soup.has_attr('srcset'):
                            image = content.select('.mlp-feature-image img')[0]['srcset']
                        elif img_soup.has_attr('data-srcset'):
                            image = content.select('.mlp-feature-image img')[0]['data-srcset']
                        elif img_soup.has_attr('src'):
                            image = content.select('.mlp-feature-image img')[0]['src']
                        if not content.select('.mlp-feature-content > h3'):
                            continue
                        img = image.split('.jpg')[0] + '.jpg'
                        title = content.select('.mlp-feature-content > h3')[0].get_text().strip()
                        description = content.select('.mlp-feature-content > p')[0].get_text().strip()
                        line = [mode['modelYear'], 'Toyota', model_name, section, title, description, img]
                        lines.append(line)
                        print(line)
                        if model_name in model_list:
                            model_list.remove(model_name)
                print(section_url)
        # lines.sort(key=lambda x: (x[0], x[2]))
        print(model_list)
        self.buick_class.write_csv(lines=lines, filename='toyota_2015_2016.csv')

    def get_2020(self):
        initial_url = 'https://www.toyota.com/'
        lines = []
        soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
        selector = '#wrapper > div.backtotop-scrollarea > section.in-page-nav > section > div > div > div > div.tcom-accordion-content > div > div.frame.js_frame ul > li.js_slide.fade> div'
        vehicles = soup.select(selector)
        for vehicle in vehicles:
            link = 'https://toyota.com' + vehicle.find_all("a", recursive=False)[0]['href']
            link_soup = BeautifulSoup(requests.get(url=link).text, 'html.parser')
            if link_soup.select(
                    '#wrapper > section:nth-child(3) > nav > div.tcom-tiered-subnav-wrapper > ul > li:nth-child(3) > a'):
                features_url = 'https://toyota.com' + link_soup.select(
                    '#wrapper > section:nth-child(3) > nav > div.tcom-tiered-subnav-wrapper > ul > li:nth-child(3) > a')[
                    0]['href']
            else:
                continue
            print(features_url)
            try:
                feature_soup = BeautifulSoup(requests.get(url=features_url).text, 'html.parser')
                year_model = \
                    feature_soup.select(
                        '#wrapper > nav > div > div.tcom-tiered-subnav-home > a.tcom-tiered-subnav-title')[
                        0].get_text().strip()
            except:
                continue
            year = year_model[:4]
            model = year_model[4:].strip()
            sections_dom = feature_soup.find_all('div', {'class': 'tcom-carousel-copy'})
            for section_dom in sections_dom:
                title = section_dom.select('.slide-title')[0].get_text().strip()
                if section_dom.select('.slide-description'):
                    description = section_dom.select('.slide-description')[0].getText().strip()
                else:
                    description = section_dom.select('.slide-short-description')[0].getText().strip()
                section = section_dom.find_previous('h2', {'class': 'category-title'}).getText().strip()
                image = 'https://toyota.com' + \
                        section_dom.find_previous('div', {'class': 'image-ct'}).find('picture').source[
                            'data-srcset'].strip()
                line = [year, 'Toyota', model, section, title, description, image]
                print(line)
                lines.append(line)
        self.buick_class.write_csv(lines=lines, filename='toyota_2020.csv')

    def get_2017_2018(self):
        for year in range(2017, 2019):
            initial_url = 'http://web.archive.org/web/%s0124003721/http://www.toyota.com/' % year
            lines = []
            for num in range(1, 5):
                soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
                print(initial_url)
                selector = '#wrapper > section.in-page-nav > div.explore-all-vehicles > div > div:nth-child(%s) > div.tcom-accordion-content > div > div > div > div > div.tcom-model-sweep-vehicle' % num
                vehicles = soup.select(selector)
                for vehicle in vehicles:
                    link = 'https://web.archive.org' + vehicle.find_all("a", recursive=False)[0]['href']
                    link_soup = BeautifulSoup(requests.get(url=link).text, 'html.parser')
                    if link_soup.select('#wrapper > nav > div > ul > li:nth-child(3) > a'):
                        features_url = 'https://web.archive.org' + \
                                       link_soup.select('#wrapper > nav > div > ul > li:nth-child(3) > a')[0]['href']
                    else:
                        continue
                    print(features_url)
                    feature_soup = BeautifulSoup(requests.get(url=features_url).text, 'html.parser')
                    if feature_soup.select(
                            '#wrapper > nav > div > div.tcom-tiered-subnav-home > a.tcom-tiered-subnav-title'):
                        year_model = feature_soup.select(
                            '#wrapper > nav > div > div.tcom-tiered-subnav-home > a.tcom-tiered-subnav-title')[
                            0].get_text().strip()
                        year = year_model[:4]
                        model = year_model[4:].strip()
                    sections_dom = feature_soup.find_all('div', {'class': 'tcom-carousel-copy'})
                    for section_dom in sections_dom:
                        title = section_dom.select('.slide-title')[0].get_text().strip()
                        description = section_dom.select('.slide-description')[0].getText().strip()
                        section = section_dom.find_previous('h2', {'class': 'category-title'}).getText().strip()
                        image_slider = section_dom.find_previous('div', {'class': 'image-ct'}).find('img')
                        if not image_slider:
                            continue
                        if image_slider.has_attr('src'):
                            image = image_slider['src']
                        elif image_slider.has_attr('data-path'):
                            image = image_slider['data-path']
                        line = [year, 'Toyota', model, section, title, description, image]
                        print(line)
                        lines.append(line)
                        self.buick_class.write_csv(lines=[line], filename='toyota_2017_2018.csv')

    def get_2019(self):
        initial_url = 'http://web.archive.org/web/20190124003721/http://www.toyota.com/'
        lines = []
        for num in range(1, 5):
            soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
            print(initial_url)
            selector = '#wrapper > section.in-page-nav > div.explore-all-vehicles > div > div:nth-child(%s) > div.tcom-accordion-content > div > div > div > div > div.tcom-model-sweep-vehicle' % num
            vehicles = soup.select(selector)
            for vehicle in vehicles:
                link = 'https://web.archive.org' + vehicle.find_all("a", recursive=False)[0]['href']
                link_soup = BeautifulSoup(requests.get(url=link).text, 'html.parser')
                if link_soup.select('#wrapper > nav > div > ul > li:nth-child(3) > a'):
                    features_url = 'https://web.archive.org' + \
                                   link_soup.select('#wrapper > nav > div > ul > li:nth-child(3) > a')[0]['href']
                else:
                    continue
                print(features_url)
                feature_soup = BeautifulSoup(requests.get(url=features_url).text, 'html.parser')
                if feature_soup.select(
                        '#wrapper > nav > div > div.tcom-tiered-subnav-home > a.tcom-tiered-subnav-title'):
                    year_model = feature_soup.select(
                        '#wrapper > nav > div > div.tcom-tiered-subnav-home > a.tcom-tiered-subnav-title')[
                        0].get_text().strip()
                    year = year_model[:4]
                    model = year_model[4:].strip()
                sections_dom = feature_soup.find_all('div', {'class': 'tcom-carousel-copy'})
                for section_dom in sections_dom:
                    title = section_dom.select('.slide-title')[0].get_text().strip()
                    description = section_dom.select('.slide-description')[0].getText().strip()
                    section = section_dom.find_previous('h2', {'class': 'category-title'}).getText().strip()
                    print(section)
                    image_ct = section_dom.find_previous('div', {'class': 'image-ct'})
                    print(image_ct)
                    if image_ct.find('picture'):
                        image = image_ct.find('picture').find('source')['data-srcset']
                    else:
                        image = image_ct.find('img')['data-path']
                    line = [year, 'Toyota', model, section, title, description, image]
                    print(line)
                    lines.append(line)
                    self.buick_class.write_csv(lines=[line], filename='toyota_2019.csv')

    def add_toyota(self):
        rows_2010_2012 = self.buick_class.read_csv(file='output/toyota_2010_2012.csv', encode='true')
        rows_2013_2014 = self.buick_class.read_csv(file='output/toyota_2013_2014.csv', encode='true')
        rows_2015_2016 = self.buick_class.read_csv(file='output/toyota_2015_2016.csv', encode='true')
        rows_2017_2018 = self.buick_class.read_csv(file='output/toyota_2017_2018.csv', encode='true')
        rows_2019 = self.buick_class.read_csv(file='output/toyota_2019.csv', encode='true')
        rows_2020 = self.buick_class.read_csv(file='output/toyota_2020.csv', encode='true')
        total_lines = []
        for row in rows_2010_2012:
            if row not in total_lines:
                total_lines.append(row)
        for row in rows_2013_2014:
            if row not in total_lines:
                total_lines.append(row)
        for row in rows_2015_2016:
            if row not in total_lines:
                total_lines.append(row)
        for row in rows_2017_2018:
            if row not in total_lines:
                total_lines.append(row)
        for row in rows_2019:
            if row not in total_lines:
                total_lines.append(row)
        for row in rows_2020:
            if row not in total_lines:
                total_lines.append(row)
        total_lines.sort(key=lambda x: (x[0], x[2]))
        self.buick_class.write_csv(lines=total_lines, filename='Toyota_Features.csv')

    def additional_2019_2020_features(self):
        chevrolet_class = Chevrolet()
        initial_url = 'https://www.toyota.com/all-vehicles/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        models_dom = initial_soup.select('#vehicle-cards .tcom-vehicle-card-image > a')
        feature_write_lines = []
        gallery_write_lines = []
        for model_dom in models_dom:
            model_link = 'https://toyota.com' + model_dom['href']
            model_soup = BeautifulSoup(requests.get(url=model_link).content, 'lxml')
            feature_url = model_soup.select('#wrapper .tcom-tiered-subnav-wrapper > ul > li:nth-child(3) > a')
            if feature_url:
                request_url = 'https://toyota.com' + feature_url[0]['href']
                print(request_url)
                feature_soup = BeautifulSoup(requests.get(url=request_url).text, 'html.parser')
                year_model = feature_soup.find('a', class_='tcom-tiered-subnav-title')
                year = year_model.text[:4]
                model = year_model.text[4:].strip()
                slides = feature_soup.find_all('h3', class_='slide-title')
                for slide in slides:
                    section = slide.find_previous('h2', class_='category-title').text.strip()
                    title = slide.get_text().strip()
                    description = slide.find_next('div', {'class': 'slide-description'}).getText().strip()
                    picture = 'https://toyota.com' + slide.find_previous('picture').source['data-srcset']
                    feature_line = [year, 'Toyota', model, section, title, description, picture.strip()]
                    print(feature_line)
                    feature_write_lines.append(feature_line)
                    section, title, description, picture = '', '', '', ''
                gallery_url = 'https://toyota.com' + \
                              model_soup.select('.tcom-tiered-subnav-wrapper > ul > li:nth-child(2) > a')[0][
                                  'href'] + '/exterior'
                gallery_soup = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml')
                pictures = gallery_soup.select('a > div.tcom-image-cta-picture > picture')
                for picture in pictures:
                    gallery_link = 'https://toyota.com' + picture.source['data-srcset']
                    gallery_section = picture.find_parent('section', {'class': 'gallery-container'})['id'].split('-')[0]
                    line = [year, 'Toyota', model, gallery_section, gallery_link.strip()]
                    print(line)
                    gallery_write_lines.append(line)
                    gallery_link, gallery_section = '', ''
                year, model = '', ''
            else:
                year = '2019'
                model = 'MIRAI'
                feature_soup = BeautifulSoup(requests.get(url=model_link).content, 'lxml')
                gallery_items = feature_soup.select('.gallery-group .gallery__item')
                for gallery_item in gallery_items:
                    section = gallery_item.parent['class'][1]
                    if section == 'all':
                        continue
                    image_url = 'https://toyota.com/mirai/' + gallery_item.img['src']
                    gallery_line = [year, 'TOYOTA', model, section, image_url.strip()]
                    print(gallery_line)
                    gallery_write_lines.append(gallery_line)
                    feature_lines = [
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Pre-Collision System with Pedestrian Detection', 'Pre-Collision System with Pedestrian Detection43 (PCS w/PD) is designed to help keep the road safe by detecting a vehicle, pedestrian or bicyclist in certain situations. The latest system has enhanced low-light capabilities for pedestrian detection. By combining millimeter-wave radar with a camera capable of certain shape recognition, the system provides an audio/visual alert, warning you of a possible collision under certain circumstances. If you don’t react, the system is designed for automatic braking47 support to help mitigate the potential for a collision.', 'https://toyota.com/mirai/assets/modules/tss/images/1024/pre-collision_System.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Dynamic Radar Cruise Control', 'Intended for highways and similar to “constant speed” cruise control, Dynamic Radar Cruise Control (DRCC)4 lets you drive at a preset speed. DRCC is designed to function at speeds of 25-110 mph and uses vehicle-to-vehicle distance control, which is designed to adjusts your speed, to help you maintain a preset distance from the vehicle ahead of you that is driving at a slower speed. DRCC uses a front-grille-mounted radar and an in-vehicle camera designed to detect vehicles and their distance. If a driver is traveling slower than you, or within your preset range, DRCC will automatically slow your vehicle down without deactivating cruise control. If DRCC determines you need to slow down more, an audio and visual alert notifies you and brakes are applied. When there’s no longer a vehicle driving slower than your set speed in front of you, DRCC will then accelerate and regular cruise control will resume.', 'https://toyota.com/mirai/assets/modules/tss/images/1024/dynamic_radar_cruise_control.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Lane Departure Alert with Steering Assist', 'Using Road Edge Detection or by detecting visible lane markings, the Lane Departure Alert with Steering Assist (LDA w/SA)7 issues both an audible alert and visual warning on the MID screen if an inadvertent lane departure is detected. If the system determines that the driver is not taking corrective steering action, the Steering Assist function is designed to initiate and provide gentle corrective steering to help keep Mirai in the lane.', 'https://toyota.com/mirai/assets/modules/tss/images/1024/alert_with_steering_assist_system.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Automatic High Beams', 'Automatic High Beams (AHB)10 are a safety system designed to help you see more clearly at night—without distracting other drivers. Designed to activate at speeds above 25 mph, AHB rely on an in-vehicle camera to help detect the headlights of oncoming vehicles and taillights of preceding vehicles, then automatically toggle between high and low beams accordingly to provide the appropriate amount of light. By using high beams more frequently, the system may allow earlier detection of pedestrians and obstacles.', 'https://toyota.com/mirai/assets/modules/tss/images/1024/automatic_high_beams.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Road Sign Assist', 'Using a forward-facing intelligent camera, Road Sign Assist45 is designed to detect speed limit signs, stop signs and yield signs, and displays them on the MID.', 'https://toyota.com/mirai/assets/modules/tss/images/1024/road_sign_assist.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Body Structure and Design', 'Mirai features a unique frame designed to distribute crash forces efficiently. In the event of a collision, the impact force is distributed around the passenger cabin and the Toyota fuel cell stack and hydrogen tanks, reducing body deformation and helping to reduce the chance of injury. The collapsible steering column also helps protect the driver by absorbing force during impact.', 'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/body-structure-and-design.jpg'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Advanced Safety System', 'Mirai is equipped with Toyota’s Star Safety System™, which is a suite of safety features for braking, stability and traction control. These include Vehicle Stability Control (VSC)1, Traction Control (TRAC), 4-wheel Anti-lock Brake System (ABS), Electronic Brake-force Distribution (EBD), Brake Assist (BA)2 and Smart Stop Technology® (SST)3.', 'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/star-safety-system.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Safety Connect®', 'With available Safety Connect®41, emergency assistance is within your reach. Via Toyota’s 24/7 call center, Safety Connect® offers subscribers helpful features such as Emergency Roadside Assistance70, Stolen Vehicle Locator71, Roadside Assistance and Automatic Collision Notification.', 'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/safety-connect.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Eight SRS Airbags', 'The cabin is equipped with a driver and front passenger Advanced Airbag System8, front seat-mounted side airbags for the driver and front passenger, front and rear side curtain airbags, plus driver knee and front passenger seat-cushion airbags. They’re all part of a system designed to help keep you safe.', 'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/eight-airbags.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Blind Spot Monitor with Rear Cross-Traffic Alert', 'When the Blind Spot Monitor (BSM)9 detects a vehicle, it illuminates a warning indicator on the appropriate sideview mirror to help let you know when it’s safe to change lanes. And when you slowly back out of a driveway or parking spot, Rear Cross-Traffic Alert (RCTA)11 provides audible and visual indicators to warn you of approaching vehicles.', 'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/blind-spot.png'],
                    ]
                    for feature_line in feature_lines:
                        feature_write_lines.append(feature_line)
        feature_write_lines.sort(key=lambda x: (x[0], x[2]))
        gallery_write_lines.sort(key=lambda x: (x[0], x[2]))
        chevrolet_class.write_csv_gallery(lines=gallery_write_lines, filename='Toyota_Galleries_2019_2020.csv')
        chevrolet_class.write_csv(lines=feature_write_lines, filename='Toyota_Features_2019_2020.csv')


class Chevrolet:
    def __init__(self):
        self.buick_class = Buick()
        self.make = 'Chevrolet'
        self.csv_header_gallery = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'GALLERY']]
        self.csv_header = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'IMAGE']]

    def write_direct_csv(self, lines, filename):
        with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(lines)
        csv_file.close()

    def write_csv(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            self.write_direct_csv(lines=self.csv_header, filename=filename)
        self.write_direct_csv(lines=lines, filename=filename)

    def write_csv_gallery(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            self.write_direct_csv(lines=self.csv_header_gallery, filename=filename)
        self.write_direct_csv(lines=lines, filename=filename)

    def get_2010(self):
        initial_url = 'http://web.archive.org/web/20100414153506/http://www.chevrolet.com/'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select(
            '#vehicles > li > div > ul > li > a')
        for brand in brands:
            url = requests.get('https://web.archive.org' + brand['href']).url
            print(url)
            soup = BeautifulSoup(requests.get(url=url).text, 'html.parser')
            model = brand['href'].split('/')[-2].upper()
            sections_content = soup.select('ul > li')
            for section_content in sections_content:
                section_dom = section_content.find('div', {'class': 'menuTitle'})
                image_dom = section_content.find('div', {'class': 'popupImage'})
                title_dom = section_content.find('div', {'class': 'popupTitle'})
                description_dom = section_content.find('div', {'class': 'popupDescription'})
                if not section_dom or not image_dom or not title_dom or not description_dom:
                    continue
                section = section_dom.get_text().strip()
                image = 'https://web.archive.org' + image_dom.get_text()
                if '.jpg' not in image:
                    continue
                title = title_dom.getText().strip()
                description = description_dom.get_text().strip()
                line = ['2010', 'Chevrolet', model, section, title, description, image]
                print(line)
                self.buick_class.write_csv(lines=[line], filename='chevrolet_2010.csv')
            # mo_sections_content = soup.select('ul > li.MO_Tile')
            # for mo_section_content in mo_sections_content:
            #     mo_image_dom = mo_section_content.find('img')
            #     mo_title_dom = mo_section_content.find('div', {'class': 'pETitle'})
            #     mo_description_dom = mo_section_content.find('div', {'class': 'pEParagraph'})
            #     if not mo_image_dom or not mo_title_dom or not mo_description_dom:
            #         continue
            #     image = 'https://web.archive.org' + mo_image_dom['src']
            #     if '.jpg' not in image:
            #         continue
            #     title = mo_title_dom.getText().strip()
            #     description = mo_description_dom.get_text().strip()
            #     line = ['2010', 'Chevrolet', model, '', title, description, image]
            #     print(line)
            #     self.buick_class.write_csv(lines=[line], filename='chevrolet_2010.csv')

    def get_2011(self):
        initial_url = 'https://web.archive.org/web/20110120062330/http://www.chevrolet.com/'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select(
            '#gnav_vehicles > ul.toplist > div > ul > li > a')
        for brand in brands:
            url = requests.get('https://web.archive.org' + brand['href']).url
            models_dom = BeautifulSoup(requests.get(url=url).text, 'html.parser')
            year_model = models_dom.select('#headBrand > li.upperHead')
            if year_model:
                gallery_url = models_dom.select('#subMenu > li:nth-child(3) > a')
                year = year_model[0].getText().strip()[:4]
                model = year_model[0].getText().strip()[4:].strip()
                modules_container = models_dom.select('#modulesMain > div.moduleContainer')
                for module_container in modules_container:
                    if module_container.find('h2', {'class': 'mainModuleHeading'}):
                        section_dom = module_container.find('h2', {'class': 'mainModuleHeading'})
                        if section_dom:
                            section = section_dom.get_text().strip()
                        else:
                            continue
                        one_thirds = module_container.find_all('div', recursive=False)
                        title_dom = module_container.find_all('div', class_='moduleSubheading')
                        titles = []
                        for title_d in title_dom:
                            titles.append(title_d.get_text().strip())
                        description_dom = []
                        for one_third in one_thirds:
                            if one_third.find('p'):
                                for div in one_third.find_all("div", {'class': 'moduleSubheading'}):
                                    div.decompose()
                                description_dom.append(one_third)
                        image_dom = module_container.select('.imageWrapper img')
                        if image_dom and title_dom and description_dom:
                            min_num = min(len(titles), len(description_dom), len(image_dom))
                        if min_num <= len(titles) and min_num <= len(description_dom) and min_num <= len(image_dom):
                            for i in range(min_num):
                                title = titles[i]
                                description = description_dom[i].getText().strip()
                                image_url = 'https://web.archive.org' + image_dom[i]['src']
                                line = [year, self.make, model, section, title, description, image_url]
                                print(line)
                                self.write_csv_gallery(lines=[line], filename='chevrolet_2011.csv')
                    else:
                        section = module_container.find_previous('h2', {'class': 'mainModuleHeading'}).getText().strip()
                        one_thirds = module_container.find_all('div', recursive=False)
                        for one_third in one_thirds:
                            image_url = ''
                            if one_third.find('div', class_='moduleSubheading'):
                                title = one_third.find('div', class_='moduleSubheading').get_text().strip()
                            if one_third.find('p'):
                                description = one_third.find('p').getText().strip()
                            if one_third.select('.imageWrapper img'):
                                image_url = 'https://web.archive.org' + one_third.select('.imageWrapper img')[0]['src']
                            if title and description and image_url:
                                line = [year, self.make, model, section, title, description, image_url]
                                print(line)
                                self.write_csv_gallery(lines=[line], filename='chevrolet_2011.csv')
                                title = ''
                                description = ''
            else:
                tool_links = models_dom.select('#toolsLinks > a.learnmore')
                for tool_link in tool_links:
                    tool_link_url = 'https://web.archive.org' + tool_link['href']
                    print(tool_link_url)
                    models_dom = BeautifulSoup(requests.get(url=tool_link_url).text, 'html.parser')
                    year_model = models_dom.select('#headBrand > li.upperHead')
                    if year_model:
                        year = year_model[0].getText().strip()[:4]
                        model = year_model[0].getText().strip()[4:].strip()
                    modules_container = models_dom.select('#modulesMain > div.moduleContainer')
                    for module_container in modules_container:
                        if module_container.find('h2', {'class': 'mainModuleHeading'}):
                            section_dom = module_container.find('h2', {'class': 'mainModuleHeading'})
                            if section_dom:
                                section = section_dom.get_text().strip()
                            else:
                                continue
                            one_thirds = module_container.find_all('div', recursive=False)
                            title_dom = module_container.find_all('div', class_='moduleSubheading')
                            titles = []
                            for title_d in title_dom:
                                titles.append(title_d.get_text().strip())
                            description_dom = []
                            for one_third in one_thirds:
                                if one_third.find('p'):
                                    for div in one_third.find_all("div", {'class': 'moduleSubheading'}):
                                        div.decompose()
                                    description_dom.append(one_third)
                            image_dom = module_container.select('.imageWrapper img')
                            if image_dom and title_dom and description_dom:
                                min_num = min(len(titles), len(description_dom), len(image_dom))
                            if min_num <= len(titles) and min_num <= len(description_dom) and min_num <= len(image_dom):
                                for i in range(min_num):
                                    title = titles[i]
                                    description = description_dom[i].getText().strip()
                                    image_url = 'https://web.archive.org' + image_dom[i]['src']
                                    line = [year, self.make, model, section, title, description, image_url]
                                    print(line)
                                    self.buick_class.write_csv(lines=[line], filename='chevrolet_2011.csv')
                        else:
                            section = module_container.find_previous('h2',
                                                                     {'class': 'mainModuleHeading'}).getText().strip()
                            one_thirds = module_container.find_all('div', recursive=False)
                            for one_third in one_thirds:
                                if one_third.find('div', class_='moduleSubheading'):
                                    title = one_third.find('div', class_='moduleSubheading').get_text().strip()
                                if one_third.find('p'):
                                    description = one_third.find('p').getText().strip()
                                if one_third.select('.imageWrapper img'):
                                    image_url = 'https://web.archive.org' + one_third.select('.imageWrapper img')[0][
                                        'src']
                                if title and description and image_url:
                                    line = [year, self.make, model, section, title, description, image_url]
                                    print(line)
                                    self.buick_class.write_csv(lines=[line], filename='chevrolet_2011.csv')
                                    title = ''
                                    description = ''
                                    image_url = ''
            print(year, model)

    def get_2011_gallery(self, filename):
        initial_url = 'https://web.archive.org/web/20110120062330/http://www.chevrolet.com/'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select(
            '#gnav_vehicles > ul.toplist > div > ul > li > a')
        for brand in brands:
            url = requests.get('https://web.archive.org' + brand['href']).url
            models_dom = BeautifulSoup(requests.get(url=url).text, 'html.parser')
            year_model = models_dom.select('#headBrand > li.upperHead')
            if year_model:
                year = year_model[0].text.strip()[:4]
                model = year_model[0].text.strip()[4:].strip()
                gallery_url = models_dom.find('span', text='Photos & Videos')
                if gallery_url:
                    gallery_url = 'https://web.archive.org' + gallery_url.parent['href']
                    print(gallery_url)
                    pictures_soup = BeautifulSoup(requests.get(url=gallery_url).content, 'html.parser')
                    galleries = pictures_soup.select('#pGalleryList .gallery ul > li')
                    for gallery in galleries:
                        gallery_link = 'https://web.archive.org' + gallery.a.img['src']
                        gallery_section = gallery.select('h5 > span')[0].text.split(' ')[-1]
                        if len(gallery_section) > 2:
                            line = [year, self.make, model, gallery_section, gallery_link]
                            print(line)
                            self.write_csv(lines=[line], filename=filename)
            else:
                tool_links = models_dom.select('#toolsLinks > a.learnmore')
                for tool_link in tool_links:
                    tool_link_url = 'https://web.archive.org' + tool_link['href']
                    models_dom = BeautifulSoup(requests.get(url=tool_link_url).text, 'html.parser')
                    year_model = models_dom.select('#headBrand > li.upperHead')
                    if not year_model:
                        continue
                    year = year_model[0].text.strip()[:4]
                    model = year_model[0].text.strip()[4:].strip()
                    gallery_url = models_dom.find('span', text='Photos & Videos')
                    if gallery_url:
                        gallery_url = 'https://web.archive.org' + gallery_url.parent['href']
                    print(gallery_url)
                    pictures_soup = BeautifulSoup(requests.get(url=gallery_url).content, 'html.parser')
                    galleries = pictures_soup.select('#pGalleryList .gallery ul > li')
                    for gallery in galleries:
                        gallery_link = 'https://web.archive.org' + gallery.a.img['src']
                        gallery_section = gallery.select('h5 > span')[0].text.split(' ')[-1]
                        if len(gallery_section) > 2:
                            line = [year, self.make, model, gallery_section, gallery_link]
                            print(line)
                            self.buick_class.write_csv(lines=[line], filename=filename)

    def get_2012(self):
        initial_url = 'https://web.archive.org/web/20120102083417/http://www.chevrolet.com/'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select(
            '#gnav_container div.narrow.bb-closed')
        for brand in brands:
            request_url = 'https://web.archive.org' + brand.find('a')['href']
            soup = BeautifulSoup(requests.get(url=request_url).content, 'html.parser')
            if soup.select('#gsnb_brand'):
                print(request_url)
                year_model = soup.select('#gsnb_brand')[0].get_text().split(' ')
                year = year_model[1].strip()
                model = year_model[13].strip()
                section_dams = soup.select('.mainModuleHeading')
                for section_dom in section_dams:
                    if len(section_dom.text) < 3 or 'What' in section_dom.text or '.' in section_dom.text:
                        continue
                    section = section_dom.text.strip()
                    wrapper_parent = section_dom.find_parent('div', {'class': 'moduleContainer'})
                    if not wrapper_parent:
                        wrapper_parent = section_dom.find_parent('div', class_='moduleWrapper')
                    if not wrapper_parent:
                        continue
                    subheadings = wrapper_parent.find_all('div', class_='moduleSubheading')
                    for subheading in subheadings:
                        title = subheading.get_text().strip()
                        image = 'https://web.archive.org' + subheading.find_previous('img')['src']
                        if '.gif' in image:
                            continue
                        description = subheading.find_next('p').text.strip()
                        line = [year, self.make, model, section, title, description, image]
                        self.buick_class.write_csv(lines=[line], filename='chevrolet_2012.csv')
                        print(line)
            else:
                learn_mores = soup.select('#toolsLinks > p.learn_more > a')
                for learn_more in learn_mores:
                    learn_url = 'https://web.archive.org' + learn_more['href']
                    learn_soup = BeautifulSoup(requests.get(url=learn_url).content, 'html.parser')
                    if learn_soup.select('#gsnb_brand'):
                        print(learn_url)
                        year_model = learn_soup.select('#gsnb_brand')[0].get_text().split(' ')
                        year = year_model[1].strip()
                        model = year_model[13].strip()
                        section_dams = learn_soup.select('.mainModuleHeading')
                        for section_dom in section_dams:
                            if len(section_dom.text) < 3 or 'What' in section_dom.text or '.' in section_dom.text:
                                continue
                            section = section_dom.text.strip()
                            wrapper_parent = section_dom.find_parent('div', {'class': 'moduleContainer'})
                            if not wrapper_parent:
                                wrapper_parent = section_dom.find_parent('div', class_='moduleWrapper')
                            subheadings = wrapper_parent.find_all('div', class_='moduleSubheading')
                            for subheading in subheadings:
                                title = subheading.get_text().strip()
                                image = 'https://web.archive.org' + subheading.find_previous('img')['src']
                                if '.gif' in image:
                                    continue
                                description = subheading.find_next('p').text.strip()
                                line = [year, self.make, model, section, title, description, image]
                                self.buick_class.write_csv(lines=[line], filename='chevrolet_2012.csv')
                                print(line)

    def get_2012_gallery(self, filename):
        initial_url = 'https://web.archive.org/web/20120102083417/http://www.chevrolet.com/'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select(
            '#gnav_container div.narrow.bb-closed')
        for brand in brands:
            request_url = 'https://web.archive.org' + brand.find('a')['href'] + 'pictures/'
            soup = BeautifulSoup(requests.get(url=request_url).content, 'html.parser')
            if soup.select('#gsnb_brand'):
                print(request_url)
                year_model = soup.select('#gsnb_brand')[0].get_text().split(' ')
                year = year_model[1].strip()
                model = year_model[13].strip()
                gallery_lis = soup.select('#htmlGallery > ul> li > a')
                for gallery_li in gallery_lis:
                    if gallery_li.select('.galleryThumb'):
                        gallery_link = 'https://web.archive.org' + gallery_li.select('img.galleryThumb')[0]['src']
                        section = gallery_li.parent.parent['class'][-1].upper()
                        line = [year, self.make, model, section, gallery_link]
                        print(line)
                        self.write_csv(lines=[line], filename=filename)
            else:
                learn_mores = soup.select('#toolsLinks > p.learn_more > a')
                for learn_more in learn_mores:
                    learn_url = 'https://web.archive.org' + learn_more['href'] + 'pictures/'
                    learn_soup = BeautifulSoup(requests.get(url=learn_url).content, 'html.parser')
                    if learn_soup.select('#gsnb_brand'):
                        print(learn_url)
                        year_model = learn_soup.select('#gsnb_brand')[0].get_text().split(' ')
                        year = year_model[1].strip()
                        model = year_model[13].strip()
                        gallery_lis = soup.select('#htmlGallery > ul> li > a')
                        for gallery_li in gallery_lis:
                            if gallery_li.select('.galleryThumb'):
                                gallery_link = 'https://web.archive.org' + gallery_li.select('img.galleryThumb')[0][
                                    'src']
                                section = gallery_li.parent.parent['class'].split(' ')[-1].upper()
                                line = [year, self.make, model, section, gallery_link]
                                print(line)
                                self.write_csv(lines=[line], filename=filename)

    def get_2013(self):
        initial_url = 'https://web.archive.org/web/20130102191357/http://www.chevrolet.com'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select('#hmc_id_0 > div > a')
        for brand in brands:
            year_model = brand.next_sibling.h3.a.text.strip()
            year = year_model[:4]
            model = year_model[4:].strip()
            request_url = 'https://web.archive.org' + brand['href']
            print(request_url)
            soup = BeautifulSoup(requests.get(url=request_url).content, 'html.parser')
            titles_dom = soup.find_all('h3', class_='pt')
            for title_dom in titles_dom:
                image_url = ''
                if not title_dom.find_previous('h2', class_='hl_t'):
                    continue
                section = title_dom.find_previous('h2', class_='hl_t').text.strip()
                title = title_dom.getText().strip()
                image_dom = self.custome_parent(title_dom).find('img')
                if image_dom and image_dom.has_attr('src'):
                    image_url = 'https://web.archive.org' + image_dom['src']
                descriptions_dom = title_dom.find_next('p').parent.find_all('p')
                description = ''
                for description_dom in descriptions_dom:
                    description += description_dom.get_text()
                line = [year, self.make, model, section, title, description.strip(), image_url]
                self.write_csv(lines=[line], filename='chevrolet_2013.csv')
                print(line)
                section = ''
                description = ''
            year = ''
            model = ''

    def get_2013_gallery(self):
        initial_url = 'https://web.archive.org/web/20130102191357/http://www.chevrolet.com/tools/help-choose-vehicles.html'
        brands = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select('#hmc_id_0 > div > a')
        for brand in brands:
            year_model = brand.next_sibling.h3.a.text.strip()
            year = year_model[:4]
            model = year_model[4:].strip()
            request_url = 'https://web.archive.org' + brand['href']
            soup = BeautifulSoup(requests.get(url=request_url).content, 'html.parser')
            gallery_url = 'https://web.archive.org' + soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0]['href']
            print(gallery_url)
            nav_pages = BeautifulSoup(requests.get(url=gallery_url.replace('pictures', 'exterior-pictures')).content, 'lxml').select('ul > li.nav_page > a')
            for nav_page in nav_pages:
                nav_link = 'https://web.archive.org' + nav_page['href']
                nav_section = nav_page.text.strip()
                thumbnail_soup = BeautifulSoup(requests.get(url=nav_link).content, 'html.parser')
                thumbnails = thumbnail_soup.select('ul.thumbnails > li')
                for thumbnail in thumbnails:
                    if not thumbnail.a:
                        continue
                    image_url = 'https://web.archive.org' + thumbnail.a['href']
                    if image_url.endswith(('.png', '.jpg', '.jpeg')):
                        gallery_line = [year, self.make, model, nav_section, image_url]
                        print(gallery_line)
                        self.write_csv_gallery(lines=[gallery_line], filename='chevrolet_gallery_2013.csv')

    def custome_parent(self, child):
        if child.find('img'):
            return child
        return self.custome_parent(child.parent)

    def get_2014(self):
        def find_section(element):
            if element.parent:
                if element.has_attr('class') and element['class'][0] == 'mod' and element['class'][1] == 'modCnt_well_1' \
                        and element['class'][2] == 'mds-cmp-content20':
                    if element.has_attr('id'):
                        return element['id']
                    else:
                        return None
                return find_section(element.parent)
            return None

        initial_url = 'http://web.archive.org/web/20140207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                'ul.ull.ui-layout-horizontal.ui-layout-left > li:nth-child(1)')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select.find('a')['href'][1:]
                bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                if not bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                titles_dom = bar_soup.find_all('h3', class_='pt')
                for title_dom in titles_dom:
                    image = ''
                    if not title_dom.find_previous('h2', class_='hl_t'):
                        continue
                    section = title_dom.find_previous('h2', class_='hl_t').text.strip()
                    section_id = find_section(title_dom)
                    if section_id and len(bar_soup.select('#%s' % section_id)) > 1:
                        search = {'href': '#%s' % section_id}
                        section_foo = bar_soup.find('a', **search)
                        if section_foo:
                            section = section_foo.get_text().strip().split(' ')[-1]
                    title = title_dom.getText().strip()
                    descriptions_dom = title_dom.find_next('p').parent.find_all('p')
                    description = ''
                    for description_dom in descriptions_dom:
                        description += description_dom.get_text()
                    image_dom = self.custome_parent(title_dom).find('img')
                    if image_dom and image_dom.has_attr('src'):
                        image = 'https://web.archive.org' + image_dom['src']
                    if not title or not description or not image:
                        continue
                    if '.html' in image:
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    self.write_csv(lines=[line], filename='chevrolet_2014.csv')
                    print(line)
                    section = ''

                accessory_url = 'https://web.archive.org' + \
                                bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[0][
                                    'href']
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).content, 'lxml')
                figures = accessory_soup.select('.accessory_item_container > ul > li > div > figure')
                for figure in figures:
                    accessory_section = figure.find_parent('li')['class'][0].upper().strip()
                    if not figure.img:
                        continue
                    image_url = 'https://web.archive.org' + figure.img['src']
                    image_title = figure.figcaption.text.strip()
                    image_description = figure.parent.find('div', {'class': 'tx'}, recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description, image_url]
                    print(accessory_line)
                    self.write_csv(lines=[accessory_line], filename='chevrolet_2014.csv')
                    image_url = ''
                    image_description = ''
                    image_title = ''
                    accessory_section = ''
                year = ''
                model = ''

    def get_2014_gallery(self):
        initial_url = 'http://web.archive.org/web/20140207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                'ul.ull.ui-layout-horizontal.ui-layout-left > li:nth-child(1)')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select.find('a')['href'][1:]
                bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                gallery_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0]['href']
                nav_pages = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml').select('ul > li.nav_page > a')
                for nav_page in nav_pages:
                    nav_section = nav_page.text.strip()
                    nav_url = 'https://web.archive.org' + nav_page['href']
                    nav_soup = BeautifulSoup(requests.get(url=nav_url).content, 'lxml')
                    nav_lis = nav_soup.select('ul.thumbnails > li > a')
                    for nav_li in nav_lis:
                        nav_image = 'https://web.archive.org' + nav_li['href']
                        if not nav_image.endswith(('jpg', 'png', 'jpeg')):
                            continue
                        gallery_line = [year, self.make, model, nav_section, nav_image]
                        print(gallery_line)
                        self.write_csv_gallery(lines=[gallery_line], filename='chevrolet_gallery_2014.csv')
                        nav_image = ''
                    nav_section = ''
                year = ''
                model = ''

    def get_2015(self):
        def find_section(element):
            if element.parent:
                if element.has_attr('class') and element['class'][0] == 'mod' and element['class'][1] == 'modCnt_well_1' \
                        and element['class'][2] == 'mds-cmp-content20':
                    if element.has_attr('id'):
                        return element['id']
                    else:
                        return None
                return find_section(element.parent)
            return None
        initial_url = 'http://web.archive.org/web/20150201225455/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        footer_ul = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul')[0]
        footer_lis = footer_ul.select('li > a')
        for footer_li in footer_lis:
            vehicle_link = 'https://web.archive.org' + footer_li['href']
            learn_more = BeautifulSoup(requests.get(url=vehicle_link).content, 'lxml')
            learn_more_links = learn_more.select('li:nth-child(1) > .cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
            for learn_more_link in learn_more_links:
                if 'https://web.archive.org' not in learn_more_link['href']:
                    model_link = 'https://web.archive.org' + learn_more_link['href']
                model_soup = BeautifulSoup(requests.get(url=model_link).content, 'lxml')
                if not model_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = model_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                titles_dom = model_soup.find_all('h3', class_='pt')
                for title_dom in titles_dom:
                    if not title_dom.find_previous('h2', class_='hl_t'):
                        continue
                    section = title_dom.find_previous('h2', class_='hl_t').text.strip()
                    section_id = find_section(title_dom)
                    if section_id and len(model_soup.select('#%s' % section_id)) > 1:
                        search = {'href': '#%s' % section_id}
                        section_foo = model_soup.find('a', **search)
                        if section_foo:
                            section = section_foo.get_text().strip().split(' ')[-1]
                    title = title_dom.get_text().strip()
                    description = ''
                    description_doms = title_dom.find_next('div', class_='fck_authorsinput tx').find_all('p')
                    for description_dom in description_doms:
                        description += description_dom.get_text()
                    image_dom = self.custome_parent(title_dom).find('img')
                    if image_dom and image_dom.has_attr('src'):
                        image = 'https://web.archive.org' + image_dom['src']
                    if not title or not description or not image:
                        continue
                    if not image.endswith(('.png', '.jpg', '.jpeg')):
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    print(line)
                    self.write_csv(lines=[line], filename='chevrolet_2015.csv')
                    section = ''

                accessory_url = 'https://web.archive.org' + \
                                model_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[
                                    0][
                                    'href']
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).content, 'lxml')
                figures = accessory_soup.select('.accessory_item_container > ul > li > div > figure')
                for figure in figures:
                    accessory_section = figure.find_parent('li')['class'][0].upper().strip()
                    if not figure.img:
                        continue
                    image_url = 'https://web.archive.org' + figure.img['src']
                    image_title = figure.figcaption.text.strip()
                    image_description = figure.parent.find('div', {'class': 'tx'},
                                                           recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description,
                                      image_url]
                    print(accessory_line)
                    self.write_csv(lines=[accessory_line], filename='chevrolet_2015.csv')
                    image_url = ''
                    image_description = ''
                    image_title = ''
                    accessory_section = ''
                year = ''
                model = ''

    def get_2015_gallery(self):
        count = []
        initial_url = 'http://web.archive.org/web/20150207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                'ul.ull.ui-layout-horizontal.ui-layout-left > li:nth-child(1)')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select.find('a')['href'][1:]
                bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                if bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.replace('THE', '').strip()
                    year = year_model[:4]
                    model = year_model[4:].strip()
                else:
                    count.append(bar_url)
                    year = '2015'
                    model = 'Sonic'
                if bar_url.endswith('.pdf'):
                    continue
                gallery_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0]['href']
                nav_pages = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml').select('ul > li.nav_page > a')
                for nav_page in nav_pages:
                    nav_section = nav_page.text.strip()
                    nav_url = 'https://web.archive.org' + nav_page['href']
                    nav_soup = BeautifulSoup(requests.get(url=nav_url).content, 'lxml')
                    nav_lis = nav_soup.select('ul.thumbnails > li > a')
                    for nav_li in nav_lis:
                        nav_image = 'https://web.archive.org' + nav_li['href']
                        if not nav_image.endswith(('.png', 'jpg', 'jpeg')):
                            continue
                        gallery_line = [year, self.make, model, nav_section, nav_image]
                        print(gallery_line)
                        self.write_csv_gallery(lines=[gallery_line], filename='chevrolet_gallery_2015.csv')
                        nav_image = ''
                    nav_section = ''
                year = ''
                model = ''
        print(count)

    def get_2016(self):
        def find_section(element):
            if element.parent:
                if element.has_attr('class') and element['class'][0] == 'mod' and element['class'][1] == 'modCnt_well_1' \
                        and element['class'][2] == 'mds-cmp-content20':
                    if element.has_attr('id'):
                        return element['id']
                    else:
                        return None
                return find_section(element.parent)
            return None

        initial_url = 'http://web.archive.org/web/20160207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                '.cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select['href'].strip()[1:]
                try:
                    bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                except:
                    continue
                if not bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                titles_dom = bar_soup.find_all('h3', class_='pt')
                for title_dom in titles_dom:
                    image = ''
                    if not title_dom.find_previous('h2', class_='hl_t'):
                        continue
                    section = title_dom.find_previous('h2', class_='hl_t').text.strip()
                    section_id = find_section(title_dom)
                    if section_id and len(bar_soup.select('#%s' % section_id)) > 1:
                        search = {'href': '#%s' % section_id}
                        section_foo = bar_soup.find('a', **search)
                        if section_foo:
                            section = section_foo.get_text().strip().split(' ')[-1]
                    title = title_dom.getText().strip()
                    descriptions_dom = title_dom.find_next('p').parent.find_all('p')
                    description = ''
                    for description_dom in descriptions_dom:
                        description += description_dom.get_text()
                    image_dom = self.custome_parent(title_dom).find('img')
                    if image_dom and image_dom.has_attr('src'):
                        if 'https://web.archive.org' in image_dom['src']:
                            image = image_dom['src']
                        else:
                            image = 'https://web.archive.org' + image_dom['src']
                    if not title or not description or not image:
                        continue
                    if not image.endswith(('.jpg', '.png', '.jpeg')):
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    self.write_csv(lines=[line], filename='chevrolet_2016.csv')
                    print(line)
                    section = ''
                print(bar_url)
                if bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a'):
                    accessory_url = 'https://web.archive.org' + \
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[0][
                                        'href']
                else:
                    accessory_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                        'href']
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).content, 'lxml')
                figures = accessory_soup.select('.accessory_item_container > ul > li > div > figure')
                for figure in figures:
                    accessory_section = figure.find_parent('li')['class'][0].upper().strip()
                    if not figure.img:
                        continue
                    if 'https://web.archive.org' in figure.img['src']:
                        image_url = figure.img['src']
                    else:
                        image_url = 'https://web.archive.org' + figure.img['src']
                    image_title = figure.figcaption.text.strip()
                    if not figure.parent.find('div', {'class': 'tx'}, recursive=False):
                        continue
                    image_description = figure.parent.find('div', {'class': 'tx'}, recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description, image_url]
                    print(accessory_line)
                    self.write_csv(lines=[accessory_line], filename='chevrolet_2016.csv')
                    image_url = ''
                    image_description = ''
                    image_title = ''
                    accessory_section = ''
                year = ''
                model = ''

    def get_2016_gallery(self):
        initial_url = 'http://web.archive.org/web/20160207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                '.cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select['href'][1:]
                try:
                    bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                except:
                    continue
                if not bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                gallery_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0]['href']
                nav_pages = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml').select('ul > li.nav_page > a')
                for nav_page in nav_pages:
                    nav_section = nav_page.text.strip()
                    nav_url = 'https://web.archive.org' + nav_page['href']
                    nav_soup = BeautifulSoup(requests.get(url=nav_url).content, 'lxml')
                    nav_lis = nav_soup.select('ul.thumbnails > li > a')
                    for nav_li in nav_lis:
                        nav_image = 'https://web.archive.org' + nav_li['href']
                        if not nav_image.endswith(('.png', '.jpg', '.jpeg')):
                            continue
                        gallery_line = [year, self.make, model, nav_section, nav_image]
                        print(gallery_line)
                        self.write_csv_gallery(lines=[gallery_line], filename='chevrolet_gallery_2016.csv')
                        nav_image = ''
                    nav_section = ''
                year = ''
                model = ''

    def get_2017(self):
        def find_section(element):
            if element.parent:
                if element.has_attr('class') and element['class'][0] == 'mod' and element['class'][1] == 'modCnt_well_1' \
                        and element['class'][2] == 'mds-cmp-content20':
                    if element.has_attr('id'):
                        return element['id']
                    else:
                        return None
                return find_section(element.parent)
            return None

        initial_url = 'http://web.archive.org/web/20170207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                '.cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select['href'].strip()[1:]
                try:
                    bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                except:
                    continue
                if not bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                titles_dom = bar_soup.find_all('h3', class_='pt')
                for title_dom in titles_dom:
                    image = ''
                    if not title_dom.find_previous('h2', class_='hl_t'):
                        continue
                    section = title_dom.find_previous('h2', class_='hl_t').text.strip()
                    section_id = find_section(title_dom)
                    if section_id and len(bar_soup.select('#%s' % section_id)) > 1:
                        search = {'href': '#%s' % section_id}
                        section_foo = bar_soup.find('a', **search)
                        if section_foo:
                            section = section_foo.get_text().strip().split(' ')[-1]
                    title = title_dom.getText().strip()
                    descriptions_dom = title_dom.find_next('p').parent.find_all('p')
                    description = ''
                    for description_dom in descriptions_dom:
                        description += description_dom.get_text()
                    image_dom = self.custome_parent(title_dom).find('img')
                    if image_dom and image_dom.has_attr('src'):
                        image = 'https://web.archive.org' + image_dom['src']
                    if not title or not description or not image:
                        continue
                    if '.html' in image:
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    self.write_csv(lines=[line], filename='chevrolet_2017.csv')
                    print(line)
                    section = ''
                print(bar_url)
                if bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a'):
                    accessory_url = 'https://web.archive.org' + \
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[0][
                                        'href']
                else:
                    accessory_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                        'href']
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).content, 'lxml')
                figures = accessory_soup.select('.accessory_item_container > ul > li > div > figure')
                for figure in figures:
                    accessory_section = figure.find_parent('li')['class'][0].upper().strip()
                    if not figure.img:
                        continue
                    image_url = 'https://web.archive.org' + figure.img['src']
                    image_title = figure.figcaption.text.strip()
                    if not figure.parent.find('div', {'class': 'tx'}, recursive=False):
                        continue
                    image_description = figure.parent.find('div', {'class': 'tx'}, recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description, image_url]
                    print(accessory_line)
                    self.write_csv(lines=[accessory_line], filename='chevrolet_2017.csv')
                    image_url = ''
                    image_description = ''
                    image_title = ''
                    accessory_section = ''
                year = ''
                model = ''

    def get_2017_gallery(self):
        initial_url = 'http://web.archive.org/web/20170207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                '.cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select['href'][1:]
                try:
                    bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                except:
                    continue
                if not bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                gallery_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0]['href']
                nav_pages = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml').select('ul > li.nav_page > a')
                for nav_page in nav_pages:
                    nav_section = nav_page.text.strip()
                    nav_url = 'https://web.archive.org' + nav_page['href']
                    nav_soup = BeautifulSoup(requests.get(url=nav_url).content, 'lxml')
                    nav_lis = nav_soup.select('ul.thumbnails > li > a')
                    for nav_li in nav_lis:
                        nav_image = 'https://web.archive.org' + nav_li['href']
                        if not nav_image.endswith(('.png', '.jpg', '.jpeg')):
                            continue
                        gallery_line = [year, self.make, model, nav_section, nav_image]
                        print(gallery_line)
                        self.write_csv_gallery(lines=gallery_line, filename='chevrolet_gallery_2017.csv')
                        nav_image = ''
                    nav_section = ''
                year = ''
                model = ''

    def get_2018(self):
        def find_section(element):
            if element.parent:
                if element.has_attr('class') and element['class'][0] == 'mod' and element['class'][1] == 'modCnt_well_1' \
                        and element['class'][2] == 'mds-cmp-content20':
                    if element.has_attr('id'):
                        return element['id']
                    else:
                        return None
                return find_section(element.parent)
            return None

        initial_url = 'http://web.archive.org/web/20180207055341/http://www.chevrolet.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        foo = initial_soup.select('#mds-area-footer > div.nav_sitemap_footer_c1 > div > div.pf6a > div > ul > li > a')
        for f in foo:
            foo_url = 'https://web.archive.org/%s' % f['href']
            foo_soup = BeautifulSoup(requests.get(url=foo_url).content, 'lxml').select(
                '.cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
            for foo_select in foo_soup:
                bar_url = 'https://web.archive.org' + foo_select['href'].strip()[1:]
                try:
                    bar_soup = BeautifulSoup(requests.get(url=bar_url).content, 'lxml')
                except:
                    continue
                if not bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)'):
                    continue
                year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[0].text.strip()
                year = year_model[:4]
                model = year_model[4:].strip()
                titles_dom = bar_soup.find_all('h3', class_='pt')
                for title_dom in titles_dom:
                    image = ''
                    if not title_dom.find_previous('h2', class_='hl_t'):
                        continue
                    section = title_dom.find_previous('h2', class_='hl_t').text.strip()
                    section_id = find_section(title_dom)
                    if section_id and len(bar_soup.select('#%s' % section_id)) > 1:
                        search = {'href': '#%s' % section_id}
                        section_foo = bar_soup.find('a', **search)
                        if section_foo:
                            section = section_foo.get_text().strip().split(' ')[-1]
                    title = title_dom.getText().strip()
                    descriptions_dom = title_dom.find_next('p').parent.find_all('p')
                    description = ''
                    for description_dom in descriptions_dom:
                        description += description_dom.get_text()
                    image_dom = self.custome_parent(title_dom).find('img')
                    if image_dom and image_dom.has_attr('src'):
                        image = 'https://web.archive.org' + image_dom['src']
                    if not title or not description or not image:
                        continue
                    if '.html' in image:
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    self.write_csv(lines=[line], filename='chevrolet_2018.csv')
                    print(line)
                    section = ''
                print(bar_url)
                if bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a'):
                    accessory_url = 'https://web.archive.org' + \
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[0][
                                        'href']
                else:
                    accessory_url = 'https://web.archive.org' + bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                        'href']
                accessory_soup = BeautifulSoup(requests.get(url=accessory_url).content, 'lxml')
                figures = accessory_soup.select('.accessory_item_container > ul > li > div > figure')
                for figure in figures:
                    accessory_section = figure.find_parent('li')['class'][0].upper().strip()
                    if not figure.img:
                        continue
                    image_url = 'https://web.archive.org' + figure.img['src']
                    image_title = figure.figcaption.text.strip()
                    if not figure.parent.find('div', {'class': 'tx'}, recursive=False):
                        continue
                    image_description = figure.parent.find('div', {'class': 'tx'}, recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description, image_url]
                    print(accessory_line)
                    self.write_csv(lines=[accessory_line], filename='chevrolet_2018.csv')
                    image_url = ''
                    image_description = ''
                    image_title = ''
                    accessory_section = ''
                year = ''
                model = ''

    def gather_gallery(self):
        self.get_2011_gallery()
        self.get_2012_gallery()


# toolsLinks > p.learn_more
class Chevrolet_count:
    def __init__(self):
        self.csv_header = [['MAKE', 'MODEL', 'ID', 'YEAR', 'GALLERY', 'PDF', 'HOW_TO_VIDEOS', 'FEATURES']]

    def write_direct_csv(self, lines, filename):
        with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(lines)
        csv_file.close()

    def write_csv(self, lines, filename):
        if not os.path.isdir('output'):
            os.mkdir('output')
        if not os.path.isfile('output/%s' % filename):
            self.write_direct_csv(lines=self.csv_header, filename=filename)
        self.write_direct_csv(lines=lines, filename=filename)

    def read_csv(self, file):
        records = []
        with open(file, "r", encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                records.append(row)
        records.pop(0)
        return records

    def count(self, file_path):
        lines = self.read_csv(file_path)
        year_array = []
        for line in lines:
            g_years = list(set(line[3].split(',')))
            p_years = list(set(line[5].split(',')))
            h_years = list(set(line[6].split(',')))
            f_years = list(set(line[7].split(',')))
            for g_year in g_years:
                if g_year not in year_array:
                    year_array.append(g_year)
            for p_year in p_years:
                if p_year not in year_array:
                    year_array.append(p_year)
            for h_year in h_years:
                if h_year not in year_array:
                    year_array.append(h_year)
            for f_year in f_years:
                if f_year not in year_array:
                    year_array.append(f_year)
        print(year_array)

        write_lines = []
        for year in range(1981, 2021):
            for line in lines:
                gallery = 0
                pdf = 0
                how_to = 0
                feature = 0
                if str(year) in line[3] or str(year) in line[5] or str(year) in line[6] or str(year) in line[7]:
                    if line[3] != 'NULL':
                        gallery = line[3].split(',').count(str(year))
                    if line[5] != 'NULL':
                        pdf = line[5].split(',').count(str(year))
                    if line[6] != 'NULL':
                        how_to = line[6].split(',').count(str(year))
                    if line[7] != 'NULL':
                        feature = line[7].split(',').count(str(year))
                    write_line = [line[0], line[1], line[2], year, gallery, pdf, how_to, feature]
                    print(write_line)
                    write_lines.append(write_line)
        write_lines.sort(key=lambda x: (x[0], x[1], x[3]))
        self.write_csv(lines=write_lines, filename='total_count.csv')
        empty_write_lines = []
        for line in lines:
            if line[3] == 'NULL' and line[5] == 'NULL' and line[6] == 'NULL' and line[7] == 'NULL':
                write_line = [line[0], line[1], line[2], '', 0, 0, 0, 0]
                empty_write_lines.append(write_line)
        empty_write_lines.sort(key=lambda x: (x[0], x[1]))
        self.write_csv(lines=empty_write_lines, filename='total_count.csv')


print("=======================Start=============================")
if __name__ == '__main__':
    ford = Ford()
    acura = Acura()
    audi = Audi()
    buick = Buick()
    toyota = Toyota()
    chevrolet = Chevrolet()
    # chevrolet.get_2017_gallery()
    chevrolet.get_2018()
    chevrolet_count = Chevrolet_count()
print("=======================The End===========================")
