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

    def get_2015(self):
        model_json_url = 'http://web.archive.org/web/20160511154040/http://www.toyota.com/ToyotaSite/rest/lscs/getDocument?templatePath=templatedata/TComVehiclesData/Series/data/CombinedSeries.xml'
        model_json = requests.get(url=model_json_url).json()['Root']['Series']
        model_list = []
        for model in model_json:
            if not model['modelName'] in model_list:
                model_list.append(model['modelName'])
        lines = []
        for mode in model_json:
            if mode['modelYear'] == 2016:
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
        print(lines)
        print(model_list)
        self.buick_class.write_csv(lines=lines, filename='toyota_2016.csv')

    def get_2017(self):
        initial_url = 'http://web.archive.org/web/20170101233213/http://www.toyota.com/'
        for num in range(1, 5):
            soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
            selector = '#wrapper > section.in-page-nav > div.explore-all-vehicles > div > div:nth-child(%s) > div.tcom-accordion-content > div > div > div > div > div.tcom-model-sweep-vehicle' % num
            vehicles = soup.select(selector)
            for vehicle in vehicles:
                link = 'https://web.aichive.org' + vehicle.find_all("a", recursive=False)[0]['href']
                model_name = vehicle.select('.tcom-model-sweep-info a')[0].getText().strip()
                model = model_name[4:].strip()
                link_soup = BeautifulSoup(requests.get(url=link).text, 'html.parser')
                sliders = link_soup.select('#wrapper > section.refresh-features-slider-container > section.tcom-carousel.refresh-features-slider')
                print(link)
                print(len(sliders))


# wrapper > section.in-page-nav > div.explore-all-vehicles > div > div:nth-child(1) > div.tcom-accordion-content > div > div > div > div > div.tcom-model-sweep-vehicle

print("=======================Start=============================")
if __name__ == '__main__':
    ford = Ford()
    acura = Acura()
    audi = Audi()
    buick = Buick()
    toyota = Toyota()
    toyota.get_2017()
print("=======================The End===========================")
