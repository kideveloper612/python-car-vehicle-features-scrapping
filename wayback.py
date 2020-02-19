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
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Pre-Collision System with Pedestrian Detection',
                         'Pre-Collision System with Pedestrian Detection43 (PCS w/PD) is designed to help keep the road safe by detecting a vehicle, pedestrian or bicyclist in certain situations. The latest system has enhanced low-light capabilities for pedestrian detection. By combining millimeter-wave radar with a camera capable of certain shape recognition, the system provides an audio/visual alert, warning you of a possible collision under certain circumstances. If you don’t react, the system is designed for automatic braking47 support to help mitigate the potential for a collision.',
                         'https://toyota.com/mirai/assets/modules/tss/images/1024/pre-collision_System.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Dynamic Radar Cruise Control',
                         'Intended for highways and similar to “constant speed” cruise control, Dynamic Radar Cruise Control (DRCC)4 lets you drive at a preset speed. DRCC is designed to function at speeds of 25-110 mph and uses vehicle-to-vehicle distance control, which is designed to adjusts your speed, to help you maintain a preset distance from the vehicle ahead of you that is driving at a slower speed. DRCC uses a front-grille-mounted radar and an in-vehicle camera designed to detect vehicles and their distance. If a driver is traveling slower than you, or within your preset range, DRCC will automatically slow your vehicle down without deactivating cruise control. If DRCC determines you need to slow down more, an audio and visual alert notifies you and brakes are applied. When there’s no longer a vehicle driving slower than your set speed in front of you, DRCC will then accelerate and regular cruise control will resume.',
                         'https://toyota.com/mirai/assets/modules/tss/images/1024/dynamic_radar_cruise_control.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Lane Departure Alert with Steering Assist',
                         'Using Road Edge Detection or by detecting visible lane markings, the Lane Departure Alert with Steering Assist (LDA w/SA)7 issues both an audible alert and visual warning on the MID screen if an inadvertent lane departure is detected. If the system determines that the driver is not taking corrective steering action, the Steering Assist function is designed to initiate and provide gentle corrective steering to help keep Mirai in the lane.',
                         'https://toyota.com/mirai/assets/modules/tss/images/1024/alert_with_steering_assist_system.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Automatic High Beams',
                         'Automatic High Beams (AHB)10 are a safety system designed to help you see more clearly at night—without distracting other drivers. Designed to activate at speeds above 25 mph, AHB rely on an in-vehicle camera to help detect the headlights of oncoming vehicles and taillights of preceding vehicles, then automatically toggle between high and low beams accordingly to provide the appropriate amount of light. By using high beams more frequently, the system may allow earlier detection of pedestrians and obstacles.',
                         'https://toyota.com/mirai/assets/modules/tss/images/1024/automatic_high_beams.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Road Sign Assist',
                         'Using a forward-facing intelligent camera, Road Sign Assist45 is designed to detect speed limit signs, stop signs and yield signs, and displays them on the MID.',
                         'https://toyota.com/mirai/assets/modules/tss/images/1024/road_sign_assist.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Body Structure and Design',
                         'Mirai features a unique frame designed to distribute crash forces efficiently. In the event of a collision, the impact force is distributed around the passenger cabin and the Toyota fuel cell stack and hydrogen tanks, reducing body deformation and helping to reduce the chance of injury. The collapsible steering column also helps protect the driver by absorbing force during impact.',
                         'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/body-structure-and-design.jpg'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Advanced Safety System',
                         'Mirai is equipped with Toyota’s Star Safety System™, which is a suite of safety features for braking, stability and traction control. These include Vehicle Stability Control (VSC)1, Traction Control (TRAC), 4-wheel Anti-lock Brake System (ABS), Electronic Brake-force Distribution (EBD), Brake Assist (BA)2 and Smart Stop Technology® (SST)3.',
                         'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/star-safety-system.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Safety Connect®',
                         'With available Safety Connect®41, emergency assistance is within your reach. Via Toyota’s 24/7 call center, Safety Connect® offers subscribers helpful features such as Emergency Roadside Assistance70, Stolen Vehicle Locator71, Roadside Assistance and Automatic Collision Notification.',
                         'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/safety-connect.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Eight SRS Airbags',
                         'The cabin is equipped with a driver and front passenger Advanced Airbag System8, front seat-mounted side airbags for the driver and front passenger, front and rear side curtain airbags, plus driver knee and front passenger seat-cushion airbags. They’re all part of a system designed to help keep you safe.',
                         'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/eight-airbags.png'],
                        ['2019', 'TOYOTA', 'MIRAI', 'SAFETY', 'Blind Spot Monitor with Rear Cross-Traffic Alert',
                         'When the Blind Spot Monitor (BSM)9 detects a vehicle, it illuminates a warning indicator on the appropriate sideview mirror to help let you know when it’s safe to change lanes. And when you slowly back out of a driveway or parking spot, Rear Cross-Traffic Alert (RCTA)11 provides audible and visual indicators to warn you of approaching vehicles.',
                         'https://toyota.com/mirai/assets/modules/car_page_safety_technology/images/blind-spot.png'],
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
            gallery_url = 'https://web.archive.org' + \
                          soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0]['href']
            print(gallery_url)
            nav_pages = BeautifulSoup(requests.get(url=gallery_url.replace('pictures', 'exterior-pictures')).content,
                                      'lxml').select('ul > li.nav_page > a')
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
                    image_description = figure.parent.find('div', {'class': 'tx'},
                                                           recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description,
                                      image_url]
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
                gallery_url = 'https://web.archive.org' + \
                              bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                  'href']
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
            learn_more_links = learn_more.select(
                'li:nth-child(1) > .cnt_btn_1.mod.modCnt_btn_1.section.mds-cmp-content02 > a')
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
                    year_model = bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dt > a:nth-child(1)')[
                        0].text.replace('THE', '').strip()
                    year = year_model[:4]
                    model = year_model[4:].strip()
                else:
                    count.append(bar_url)
                    year = '2015'
                    model = 'Sonic'
                if bar_url.endswith('.pdf'):
                    continue
                gallery_url = 'https://web.archive.org' + \
                              bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                  'href']
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
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[
                                        0][
                                        'href']
                else:
                    accessory_url = 'https://web.archive.org' + \
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[
                                        0][
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
                    image_description = figure.parent.find('div', {'class': 'tx'},
                                                           recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description,
                                      image_url]
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
                gallery_url = 'https://web.archive.org' + \
                              bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                  'href']
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
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd >ul > li:nth-child(4) > a')[
                                        0][
                                        'href']
                else:
                    accessory_url = 'https://web.archive.org' + \
                                    bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[
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
                    if not figure.parent.find('div', {'class': 'tx'}, recursive=False):
                        continue
                    image_description = figure.parent.find('div', {'class': 'tx'},
                                                           recursive=False).span.get_text().strip()
                    accessory_line = [year, self.make, model, accessory_section, image_title, image_description,
                                      image_url]
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
                gallery_url = 'https://web.archive.org' + \
                              bar_soup.select('#mds-cmp-2ndlevelnavigation > dl > dd > ul > li:nth-child(2) > a')[0][
                                  'href']
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
                        self.write_csv_gallery(lines=[gallery_line], filename='chevrolet_gallery_2017.csv')
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

        initial_url = 'https://web.archive.org/web/20170408225805/http://www.chevrolet.com/navigation/navigationflyouts/vehicles.html'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        vehicle_links = initial_soup.select('.q-nav-vehicle-selector > div > div > div')
        link_list = []
        for vehicle_link in vehicle_links:
            if not vehicle_link.find('a').has_attr('href'):
                continue
            link = 'https://web.archive.org' + vehicle_link.find('a')['href']
            if link in link_list:
                continue
            link_list.append(link)
            year_model = vehicle_link.find('img')['alt']
            year = year_model[:4]
            model = year_model[4:].strip()
            link_soup = BeautifulSoup(requests.get(url=link).content, 'lxml')
            headlines = link_soup.select('.q-headline2 ')
            for headline in headlines:
                section = headline.find_previous('div', class_='q-sec-anchor')['id']
                title = headline.get_text().strip()
                descriptions_dom = headline.find_next('p').parent.find_all('p')
                for description_dom in descriptions_dom:
                    description = description_dom.get_text()
                if self.custome_parent(headline).find('img').has_attr('src'):
                    image = 'https://web.archive.org' + self.custome_parent(headline).find('img')['src']
                if self.custome_parent(headline).find('img').has_attr('srcset'):
                    image = 'https://web.archive.org' + self.custome_parent(headline).find('img')['srcset']
                line = [year, self.make, model, section, title, description, image]
                print(line)
                self.write_csv(lines=[line], filename='chevrolet_2018.csv')

    def get_description(self, element):
        count = 0
        for test in element.next_elements:
            print(test)
            count += 1
            if count > 15:
                exit()
        if element.next_element.text:
            return element.next_element
        return element.next_element.next_element

    def get_2019_2020(self):
        initial_url = 'https://www.chevrolet.com/navigation/navigationflyouts/vehicles.html'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        vehicle_links = initial_soup.select('.q-vehicle-selector-row a')
        for vehicle_link in vehicle_links:
            link = 'https://chevrolet.com' + vehicle_link['href']
            soup = BeautifulSoup(requests.get(url=link).content, 'lxml')
            print(link)
            if soup.select('.q-year-toggle-list .q-year-toggle-list-item.active'):
                year = soup.select('.q-year-toggle-list .q-year-toggle-list-item.active')[0].text.strip()
                model = vehicle_link.select('.q-vehicle-info-tile-type')[0].text.strip()
                titles_dom = soup.select('[class*="q-headline"]')
                for title_dom in titles_dom:
                    if title_dom.find_parent('footer'):
                        continue
                    if not title_dom.find_previous('h2', {'class': re.compile('q-descriptive2')}):
                        continue
                    section = title_dom.find_previous('h2', {'class': re.compile('q-descriptive2')}).text.strip()
                    title = title_dom.text.strip().replace(u'\xa0', '').replace(u'\n', '')
                    description = title_dom.find_next('div', attrs={'class': re.compile(u'q-text')}).get_text().strip()
                    if 'https://chevrolet.com' not in self.custome_parent(title_dom).find('img')['src']:
                        image = 'https://chevrolet.com' + self.custome_parent(title_dom).find('img')['src']
                    else:
                        image = self.custome_parent(title_dom).find('img')['src']
                    if not section or not title or not description or not image:
                        continue
                    if len(section.split(' ')) > 1:
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    print(line)
                    self.write_csv(lines=[line], filename='chevrolet_2019_2020.csv')
                slash_positions = [m.start() for m in re.finditer('/', link)]
                previous_link = link[:slash_positions[-1] + 1] + 'previous-year' + link[slash_positions[-1]:]
                previous_soup = BeautifulSoup(requests.get(url=previous_link).content, 'lxml')
                if previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active'):
                    previous_year = previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active')[0].text.strip()
                    titles_dom = soup.select('[class*="q-headline"]')
                    for title_dom in titles_dom:
                        if title_dom.find_parent('footer'):
                            continue
                        if not title_dom.find_previous('h2', {'class': re.compile('q-descriptive2')}):
                            continue
                        section = title_dom.find_previous('h2', {'class': re.compile('q-descriptive2')}).text.strip()
                        title = title_dom.text.strip().replace(u'\xa0', '').replace(u'\n', '')
                        description = title_dom.find_next('div',
                                                          attrs={'class': re.compile(u'q-text')}).get_text().strip()
                        if 'https://chevrolet.com' not in self.custome_parent(title_dom).find('img')['src']:
                            image = 'https://chevrolet.com' + self.custome_parent(title_dom).find('img')['src']
                        else:
                            image = self.custome_parent(title_dom).find('img')['src']
                        if not section or not title or not description or not image:
                            continue
                        if len(section.split(' ')) > 1:
                            continue
                        line = [previous_year, self.make, model, section, title, description.strip(), image]
                        print(line)
                        self.write_csv(lines=[line], filename='chevrolet_2019_2020.csv')
            else:
                model = vehicle_link.select('.q-vehicle-info-tile-type')[0].text.strip()
                if soup.title.text[:7] == 'All-New':
                    year = soup.title.text.split(' ')[1]
                    model = soup.select('h1.q-invert:nth-child(1)')[0].text.strip()
                elif soup.title.text[:11] == 'Introducing':
                    year = soup.title.text.split(' ')[2]
                elif soup.title.text[:5] == 'Chevy':
                    year = '2020'
                elif soup.title.text[:7] == 'Engines':
                    continue
                else:
                    year = soup.title.text[:4]
                if '\n' in model:
                    model = model[:model.find('\n')]
                model = model.replace(u'ALL-NEW', '').replace(u'All-New', '').replace('2020', '').replace('2021', '').strip()
                titles_dom = soup.select('[class*="q-headline"]')
                for title_dom in titles_dom:
                    if title_dom.find_parent('footer'):
                        continue
                    if not title_dom.find_previous('h2', {'class': re.compile('q-descriptive2')}):
                        continue
                    section = title_dom.find_previous('h2', {'class': re.compile('q-descriptive2')}).text.strip()
                    title = title_dom.text.strip().replace(u'\xa0', '').replace(u'\n', '')
                    description = title_dom.find_next('div', attrs={'class': re.compile(u'q-text')}).get_text().strip()
                    if 'https://chevrolet.com' not in self.custome_parent(title_dom).find('img')['src']:
                        image = 'https://chevrolet.com' + self.custome_parent(title_dom).find('img')['src']
                    else:
                        image = self.custome_parent(title_dom).find('img')['src']
                    if not section or not title or not description or not image:
                        continue
                    if len(section.split(' ')) > 1:
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    print(line)
                    self.write_csv(lines=[line], filename='chevrolet_2019_2020.csv')

    def get_2019_2020_gallery(self):
        initial_url = 'https://www.chevrolet.com/navigation/navigationflyouts/vehicles.html'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        vehicle_links = initial_soup.select('.q-vehicle-selector-row a')
        for vehicle_link in vehicle_links:
            link = 'https://chevrolet.com' + vehicle_link['href']
            soup = BeautifulSoup(requests.get(url=link).content, 'lxml')
            print(link)
            if soup.select('.q-year-toggle-list .q-year-toggle-list-item.active'):
                year = soup.select('.q-year-toggle-list .q-year-toggle-list-item.active')[0].text.strip()
                model = vehicle_link.select('.q-vehicle-info-tile-type')[0].text.strip()
                all_div = soup.findAll('div')
                for div in all_div:
                    if div.has_attr('data-gallery-layer'):
                        gallery_url = 'https://www.chevrolet.com' + div['data-gallery-layer'] + '/jcr:content/content.html'
                        break
                gallery_soup = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml')
                lis = gallery_soup.select('ul > li')
                for li in lis:
                    image_url = 'https://chevrolet.com' + li.img['src']
                    section = li.find_previous('h1').span.text.strip()
                    line = [year, self.make, model, section, image_url]
                    print(line)
                    self.write_csv(lines=[line], filename='chevrolet_gallery_2019_2020.csv')
                print(gallery_url)
                slash_positions = [m.start() for m in re.finditer('/', link)]
                previous_link = link[:slash_positions[-1] + 1] + 'previous-year' + link[slash_positions[-1]:]
                previous_soup = BeautifulSoup(requests.get(url=previous_link).content, 'lxml')
                if previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active'):
                    previous_year = previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active')[0].text.strip()
                    all_div_previous = soup.findAll('div')
                    for div_previous in all_div_previous:
                        if div_previous.has_attr('data-gallery-layer'):
                            gallery_url_previous = 'https://www.chevrolet.com' + div[
                                'data-gallery-layer'] + '/jcr:content/content.html'
                            break
                    gallery_soup_previous = BeautifulSoup(requests.get(url=gallery_url_previous).content, 'lxml')
                    lis_previous = gallery_soup_previous.select('ul > li')
                    for li_previous in lis_previous:
                        image_url_previous = 'https://chevrolet.com' + li_previous.img['src']
                        section_previous = li_previous.find_previous('h1').span.text.strip()
                        line_previous = [previous_year, self.make, model, section_previous, image_url_previous]
                        print(line_previous)
                        self.write_csv(lines=[line_previous], filename='chevrolet_gallery_2019_2020.csv')
                    print(gallery_url_previous)
            else:
                model = vehicle_link.select('.q-vehicle-info-tile-type')[0].text.strip()
                if soup.title.text[:7] == 'All-New':
                    year = soup.title.text.split(' ')[1]
                    model = soup.select('h1.q-invert:nth-child(1)')[0].text.strip()
                elif soup.title.text[:11] == 'Introducing':
                    year = soup.title.text.split(' ')[2]
                elif soup.title.text[:5] == 'Chevy':
                    year = '2020'
                elif soup.title.text[:7] == 'Engines':
                    continue
                else:
                    year = soup.title.text[:4]
                if '\n' in model:
                    model = model[:model.find('\n')]
                model = model.replace(u'ALL-NEW', '').replace(u'All-New', '').replace('2020', '').replace('2021', '').strip()
                all_div_else = soup.findAll('div')
                for div_else in all_div_else:
                    try:
                        if div_else.has_attr('data-gallery-layer'):
                            gallery_url_else = 'https://www.chevrolet.com' + div[
                                'data-gallery-layer'] + '/jcr:content/content.html'
                            break
                    except:
                        continue
                gallery_soup_else = BeautifulSoup(requests.get(url=gallery_url_else).content, 'lxml')
                lis_else = gallery_soup_else.select('ul > li')
                for li_else in lis_else:
                    image_url_else = 'https://chevrolet.com' + li_else.img['src']
                    section_else = li_else.find_previous('h1').span.text.strip()
                    line_else = [year, self.make, model, section_else, image_url_else]
                    print(line_else)
                    self.write_csv(lines=[line_else], filename='chevrolet_gallery_2019_2020.csv')
                print(gallery_url_else)

    def get_2018_addition(self):
        initial_url = 'http://web.archive.org/web/20180821111847/https://www.chevrolet.com'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        footer_s = initial_soup.select('.q-margin-base.q-content-well a', limit=11)
        urls = []
        request_urls = ['https://web.archive.org/web/20180807203527/https://www.chevrolet.com/cars/cruze-small-car', 'https://web.archive.org/web/20180821111848/https://www.chevrolet.com/cars/malibu-mid-size-car', 'https://web.archive.org/web/20180821111743/https://www.chevrolet.com/cars/impala-full-size-car', 'https://web.archive.org/web/20180824221820/https://www.chevrolet.com/connectivity-and-technology', 'https://web.archive.org/web/20180812125920/http://www.chevrolet.com/connectivity-and-technology', 'https://web.archive.org/web/20180823154333/https://www.chevrolet.com/cars/spark-subcompact-car', 'https://web.archive.org/web/20190320084813/https://www.chevrolet.com/cars/sonic-small-car', 'https://web.archive.org/web/20180515211729/http://www.chevrolet.com/corvette-life/engines', 'https://web.archive.org/web/20180813151203/https://www.chevrolet.com/performance-data-recorder', 'https://web.archive.org/web/20180817144322/https://www.chevrolet.com/suvs/traverse-mid-size-suv', 'https://web.archive.org/web/20181121001521/https://www.chevrolet.com/suvs/equinox-small-suv', 'https://web.archive.org/web/20180802034342/https://www.chevrolet.com/suvs/trax-compact-suv', 'https://web.archive.org/web/20180617042519/https://www.chevrolet.com/suvs/suburban-large-suv', 'https://web.archive.org/web/20180919222723/https://www.chevrolet.com/suvs/tahoe-full-size-suv', 'https://web.archive.org/web/20180817011125/https://www.chevrolet.com/trucks/colorado-mid-size-truck', 'https://web.archive.org/web/20180809024025/https://www.chevrolet.com/trucks/silverado-1500-pickup-truck', 'https://web.archive.org/web/20180611081244/http://www.chevrolet.com/trucks/silverado-2500hd-3500hd-heavy-duty-trucks', 'https://web.archive.org/web/20180612110706/http://www.chevrolet.com/commercial/silverado-3500hd-chassis-cab', 'https://web.archive.org/web/20180614224657/http://www.chevrolet.com/truck-life/centennial-edition', 'http://web.archive.org/web/20180808005354/http://www.chevytrucklegends.com/us/en/index.html', 'https://web.archive.org/web/20180820002310/https://www.chevrolet.com/cars/bolt-ev-electric-car', 'https://web.archive.org/web/20180820002310/https://www.chevrolet.com/hybrids/volt-plug-in-hybrid', 'https://web.archive.org/web/20180821111847/https://www.chevrolet.com/car#hybrids/malibu-mid-size-car%23hybrid', 'https://web.archive.org/web/20180815131458/https://www.chevrolet.com/commercial/express-cargo-van', 'https://web.archive.org/web/20180611081229/http://www.chevrolet.com/commercial/express-passenger-van', 'https://web.archive.org/web/20180423234756/http://www.chevrolet.com/previous-year/colorado-work-truck', 'https://web.archive.org/web/20180603155210/http://www.chevrolet.com/commercial/silverado-1500-work-truck', 'https://web.archive.org/web/20180612122405/http://www.chevrolet.com/commercial/silverado-2500hd-3500hd-work-truck', 'https://web.archive.org/web/20181011201905/https://www.chevrolet.com/commercial/low-cab-forward-cab-over-truck', 'https://web.archive.org/web/20180522172036/http://www.chevrolet.com/commercial/express-cutaway-van', 'https://web.archive.org/web/20180724095528/https://www.chevrolet.com/discontinued-vehicles/city-express', 'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial', 'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial/cars-crossovers-suvs#suv', 'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial/cars-crossovers-suvs#crossover', 'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial/cars-crossovers-suvs#car', 'http://web.archive.org/web/20170910113357/http://www.gmfleet.com/chevrolet-business-choice-offers-incentives.html?cmp=Lowes_Referral', 'https://web.archive.org/web/20180606190838/http://www.chevrolet.com/tax-deductions', 'https://web.archive.org/web/20180802033752/https://www.chevrolet.com/commercial/business-elite', 'https://web.archive.org/web/20180606052039/http://www.chevrolet.com/commercial/commercial-link', 'http://web.archive.org/web/20190513084838/https://www.gmfleet.com/chevrolet-fleet-vehicles.html', 'https://web.archive.org/web/20180613210519/http://www.chevrolet.com/commercial']
        # for footer_foo in footer_s:
        #     foo_link = 'http://web.archive.org' + footer_foo['href']
        #     foo_soup = BeautifulSoup(requests.get(url=foo_link).content, 'lxml')
        #     explores = foo_soup.select('a[class*="stat-button-link"]')
        #     for explore in explores:
        #         if not 'Explore' in explore.text:
        #             continue
        #         if 'http://web.archive.org' in explore['href']:
        #             explore_url = explore['href']
        #         else:
        #             explore_url = 'https://web.archive.org' + explore['href']
        #         if 'previous-year' in explore_url:
        #             explore_url = explore_url.replace('previous-year', explore_url.split('-')[-1] + 's')
        #         if explore_url == 'https://web.archive.org/web/20180823035642/https://www.chevrolet.com/commercial':
        #             commercial = BeautifulSoup(requests.get(url=explore_url).text, 'lxml')
        #             overviews = commercial.select('a[class*="stat-button-link"]')
        #             for overview in overviews:
        #                 if 'Overview' in overview.text:
        #                     commercial_url = 'https://web.archive.org' + overview['href']
        #                     urls.append(commercial_url)
        #                     continue
        #         urls.append(explore_url)
        # for url in urls:
        #     url = requests.get(url=url).url
        #     if url in request_urls:
        #         continue
        #     request_urls.append(url)
        #     print(url)

        for request_url in request_urls:
            print(request_url)
            url_soup = BeautifulSoup(requests.get(url=request_url).content, 'html.parser')
            if url_soup.select('li.q-year-toggle-list-item a'):
                links = url_soup.select('li.q-year-toggle-list-item.active a')
                for link in links:
                    request_link = 'https://web.archive.org' + link['href']
                    request_soup = BeautifulSoup(requests.get(url=request_link).content, 'lxml')
                    print(request_soup.select('li.q-year-toggle-list-item.active a'))
                    year = request_soup.select('li.q-year-toggle-list-item.active a')[0].get_text().strip()
                    model = request_soup.select('.q-dropdown-arrow.q-js-button-text')[0].getText().strip()
                    titles_dom = request_soup.select('[class*="q-headline"]')
                    for title_dom in titles_dom:
                        if title_dom.find_parent('footer'):
                            continue
                        if not title_dom.find_previous('div', {'class': 'q-sec-anchor'}):
                            continue
                        section = title_dom.find_previous('div', {'class': 'q-sec-anchor'})['id'].strip()
                        title = title_dom.text.strip().replace(u'\xa0', '').replace(u'\n', '')
                        description = title_dom.find_next('div',
                                                          attrs={'class': re.compile(u'q-text')}).get_text().strip()
                        if 'https://chevrolet.com' not in self.custome_parent(title_dom).find('img')['src']:
                            image = 'https://chevrolet.com' + self.custome_parent(title_dom).find('img')['src']
                        else:
                            image = self.custome_parent(title_dom).find('img')['src']
                        if not section or not title or not description or not image:
                            continue
                        if len(section.split(' ')) > 1:
                            continue
                        line = [year, self.make, model, section, title, description.strip(), image]
                        print(line)
                        self.write_csv(lines=[line], filename='chevrolet_2018_addition.csv')
                    slash_positions = [m.start() for m in re.finditer('/', request_link)]
                    previous_link = request_link[:slash_positions[-1] + 1] + 'previous-year' + request_link[slash_positions[-1]:]
                    previous_soup = BeautifulSoup(requests.get(url=previous_link).content, 'lxml')
                    if previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active'):
                        previous_year = previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active')[
                            0].text.strip()
                        titles_dom = request_soup.select('[class*="q-headline"]')
                        for title_dom in titles_dom:
                            if title_dom.find_parent('footer'):
                                continue
                            if not title_dom.find_previous('div', {'class': 'q-sec-anchor'}):
                                continue
                            section = title_dom.find_previous('div',
                                                              {'class': 'q-sec-anchor'})['id'].strip()
                            title = title_dom.text.strip().replace(u'\xa0', '').replace(u'\n', '')
                            description = title_dom.find_next('div',
                                                              attrs={'class': re.compile(u'q-text')}).get_text().strip()
                            if 'https://chevrolet.com' not in self.custome_parent(title_dom).find('img')['src']:
                                image = 'https://chevrolet.com' + self.custome_parent(title_dom).find('img')['src']
                            else:
                                image = self.custome_parent(title_dom).find('img')['src']
                            if not section or not title or not description or not image:
                                continue
                            if len(section.split(' ')) > 1:
                                continue
                            line = [previous_year, self.make, model, section, title, description.strip(), image]
                            print(line)
                            self.write_csv(lines=[line], filename='chevrolet_2018_addition.csv')
            else:
                if not url_soup.select('h1.q-invert'):
                    continue
                model = url_soup.select('h1.q-invert')[0].get_text().strip()
                year = url_soup.title.text[:4]
                titles_dom = url_soup.select('[class*="q-headline"]')
                for title_dom in titles_dom:
                    if title_dom.find_parent('footer'):
                        continue
                    if not title_dom.find_previous('div', {'class': 'q-sec-anchor'}):
                        continue
                    section = title_dom.find_previous('div', {'class': 'q-sec-anchor'})['id']
                    title = title_dom.text.strip().replace(u'\xa0', '').replace(u'\n', '')
                    description = title_dom.find_next('div',
                                                      attrs={'class': re.compile(u'q-text')}).get_text().strip()
                    if 'https://chevrolet.com' not in self.custome_parent(title_dom).find('img')['src']:
                        image = 'https://chevrolet.com' + self.custome_parent(title_dom).find('img')['src']
                    else:
                        image = self.custome_parent(title_dom).find('img')['src']
                    if not section or not title or not description or not image:
                        continue
                    if len(section.split(' ')) > 1:
                        continue
                    line = [year, self.make, model, section, title, description.strip(), image]
                    print(line)
                    self.write_csv(lines=[line], filename='chevrolet_2018_addition.csv')

    def get_2018_gallery(self):
        request_urls = ['https://web.archive.org/web/20180807203527/https://www.chevrolet.com/cars/cruze-small-car',
                        'https://web.archive.org/web/20180821111848/https://www.chevrolet.com/cars/malibu-mid-size-car',
                        'https://web.archive.org/web/20180821111743/https://www.chevrolet.com/cars/impala-full-size-car',
                        'https://web.archive.org/web/20180824221820/https://www.chevrolet.com/connectivity-and-technology',
                        'https://web.archive.org/web/20180812125920/http://www.chevrolet.com/connectivity-and-technology',
                        'https://web.archive.org/web/20180823154333/https://www.chevrolet.com/cars/spark-subcompact-car',
                        'https://web.archive.org/web/20190320084813/https://www.chevrolet.com/cars/sonic-small-car',
                        'https://web.archive.org/web/20180515211729/http://www.chevrolet.com/corvette-life/engines',
                        'https://web.archive.org/web/20180813151203/https://www.chevrolet.com/performance-data-recorder',
                        'https://web.archive.org/web/20180817144322/https://www.chevrolet.com/suvs/traverse-mid-size-suv',
                        'https://web.archive.org/web/20181121001521/https://www.chevrolet.com/suvs/equinox-small-suv',
                        'https://web.archive.org/web/20180802034342/https://www.chevrolet.com/suvs/trax-compact-suv',
                        'https://web.archive.org/web/20180617042519/https://www.chevrolet.com/suvs/suburban-large-suv',
                        'https://web.archive.org/web/20180919222723/https://www.chevrolet.com/suvs/tahoe-full-size-suv',
                        'https://web.archive.org/web/20180817011125/https://www.chevrolet.com/trucks/colorado-mid-size-truck',
                        'https://web.archive.org/web/20180809024025/https://www.chevrolet.com/trucks/silverado-1500-pickup-truck',
                        'https://web.archive.org/web/20180611081244/http://www.chevrolet.com/trucks/silverado-2500hd-3500hd-heavy-duty-trucks',
                        'https://web.archive.org/web/20180612110706/http://www.chevrolet.com/commercial/silverado-3500hd-chassis-cab',
                        'https://web.archive.org/web/20180614224657/http://www.chevrolet.com/truck-life/centennial-edition',
                        'http://web.archive.org/web/20180808005354/http://www.chevytrucklegends.com/us/en/index.html',
                        'https://web.archive.org/web/20180820002310/https://www.chevrolet.com/cars/bolt-ev-electric-car',
                        'https://web.archive.org/web/20180820002310/https://www.chevrolet.com/hybrids/volt-plug-in-hybrid',
                        'https://web.archive.org/web/20180821111847/https://www.chevrolet.com/car#hybrids/malibu-mid-size-car%23hybrid',
                        'https://web.archive.org/web/20180815131458/https://www.chevrolet.com/commercial/express-cargo-van',
                        'https://web.archive.org/web/20180611081229/http://www.chevrolet.com/commercial/express-passenger-van',
                        'https://web.archive.org/web/20180423234756/http://www.chevrolet.com/previous-year/colorado-work-truck',
                        'https://web.archive.org/web/20180603155210/http://www.chevrolet.com/commercial/silverado-1500-work-truck',
                        'https://web.archive.org/web/20180612122405/http://www.chevrolet.com/commercial/silverado-2500hd-3500hd-work-truck',
                        'https://web.archive.org/web/20181011201905/https://www.chevrolet.com/commercial/low-cab-forward-cab-over-truck',
                        'https://web.archive.org/web/20180522172036/http://www.chevrolet.com/commercial/express-cutaway-van',
                        'https://web.archive.org/web/20180724095528/https://www.chevrolet.com/discontinued-vehicles/city-express',
                        'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial',
                        'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial/cars-crossovers-suvs#suv',
                        'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial/cars-crossovers-suvs#crossover',
                        'https://web.archive.org/web/20180821174556/https://www.chevrolet.com/commercial/cars-crossovers-suvs#car',
                        'http://web.archive.org/web/20170910113357/http://www.gmfleet.com/chevrolet-business-choice-offers-incentives.html?cmp=Lowes_Referral',
                        'https://web.archive.org/web/20180606190838/http://www.chevrolet.com/tax-deductions',
                        'https://web.archive.org/web/20180802033752/https://www.chevrolet.com/commercial/business-elite',
                        'https://web.archive.org/web/20180606052039/http://www.chevrolet.com/commercial/commercial-link',
                        'http://web.archive.org/web/20190513084838/https://www.gmfleet.com/chevrolet-fleet-vehicles.html',
                        'https://web.archive.org/web/20180613210519/http://www.chevrolet.com/commercial']
        for request_url in request_urls:
            print(request_url)
            url_soup = BeautifulSoup(requests.get(url=request_url).content, 'html.parser')
            if url_soup.select('li.q-year-toggle-list-item a'):
                links = url_soup.select('li.q-year-toggle-list-item.active a')
                for link in links:
                    request_link = 'https://web.archive.org' + link['href']
                    request_soup = BeautifulSoup(requests.get(url=request_link).content, 'lxml')
                    print(request_soup.select('li.q-year-toggle-list-item.active a'))
                    year = request_soup.select('li.q-year-toggle-list-item.active a')[0].get_text().strip()
                    model = request_soup.select('.q-dropdown-arrow.q-js-button-text')[0].getText().strip()
                    all_div = request_soup.findAll('div')
                    for div in all_div:
                        if div.has_attr('data-gallery-layer'):
                            gallery_url = 'https://www.chevrolet.com' + div[
                                'data-gallery-layer'] + '/jcr:content/content.html'
                            break
                    gallery_soup = BeautifulSoup(requests.get(url=gallery_url).content, 'lxml')
                    lis = gallery_soup.select('ul > li')
                    for li in lis:
                        image_url = 'https://chevrolet.com' + li.img['src']
                        section = li.find_previous('h1').span.text.strip()
                        line = [year, self.make, model, section, image_url]
                        print(line)
                        self.write_csv(lines=[line], filename='chevrolet_gallery_2018.csv')
                    print(gallery_url)
                    slash_positions = [m.start() for m in re.finditer('/', request_link)]
                    previous_link = request_link[:slash_positions[-1] + 1] + 'previous-year' + request_link[
                                                                                               slash_positions[-1]:]
                    previous_soup = BeautifulSoup(requests.get(url=previous_link).content, 'lxml')
                    if previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active'):
                        previous_year = previous_soup.select('.q-year-toggle-list .q-year-toggle-list-item.active')[
                            0].text.strip()
                        all_div_previous = previous_soup.findAll('div')
                        for div_previous in all_div_previous:
                            if div_previous.has_attr('data-gallery-layer'):
                                gallery_url_previous = 'https://www.chevrolet.com' + div[
                                    'data-gallery-layer'] + '/jcr:content/content.html'
                                break
                        gallery_soup_previous = BeautifulSoup(requests.get(url=gallery_url_previous).content, 'lxml')
                        lis_previous = gallery_soup_previous.select('ul > li')
                        for li_previous in lis_previous:
                            image_url_previous = 'https://chevrolet.com' + li_previous.img['src']
                            section_previous = li_previous.find_previous('h1').span.text.strip()
                            line_previous = [previous_year, self.make, model, section_previous, image_url_previous]
                            print(line_previous)
                            self.write_csv(lines=[line_previous], filename='chevrolet_gallery_2018.csv')
                        print(gallery_url_previous)
            else:
                if not url_soup.select('h1.q-invert'):
                    continue
                model = url_soup.select('h1.q-invert')[0].get_text().strip()
                year = url_soup.title.text[:4]
                all_div_else = url_soup.findAll('div')
                for div_else in all_div_else:
                    try:
                        if div_else.has_attr('data-gallery-layer'):
                            gallery_url_else = 'https://www.chevrolet.com' + div[
                                'data-gallery-layer'] + '/jcr:content/content.html'
                            break
                    except:
                        continue
                gallery_soup_else = BeautifulSoup(requests.get(url=gallery_url_else).content, 'lxml')
                lis_else = gallery_soup_else.select('ul > li')
                for li_else in lis_else:
                    image_url_else = 'https://chevrolet.com' + li_else.img['src']
                    section_else = li_else.find_previous('h1').span.text.strip()
                    line_else = [year, self.make, model, section_else, image_url_else]
                    print(line_else)
                    self.write_csv(lines=[line_else], filename='chevrolet_gallery_2018.csv')
                print(gallery_url_else)

    def read_csv(self, filepath):
        records = []
        with open(filepath, "r", encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                records.append(row)
        records.pop(0)
        return records

    def all_collect(self):
        from os import listdir
        from os.path import isfile, join
        feature_files = [join('output\\Chevrolet\\Features', f) for f in listdir('output\\Chevrolet\\Features') if isfile(join('output\\Chevrolet\\Features', f))]
        gallery_files = [join('output\\Chevrolet\\Gallery', f) for f in listdir('output\\Chevrolet\\Gallery') if
                         isfile(join('output\\Chevrolet\\Gallery', f))]
        feature_lines = []
        gallery_lines = []
        for file in feature_files:
            lines = self.buick_class.read_csv(file, encode='true')
            for line in lines:
                feature_lines.append(line)
                print(line)
        for file in gallery_files:
            lines = self.read_csv(file)
            for line in lines:
                gallery_lines.append(line)
                print(line)
        feature_lines.sort(key=lambda x: (x[0], x[2], x[3]))
        gallery_lines.sort(key=lambda x: (x[0], x[2], x[3]))
        print(gallery_lines)
        print(feature_lines)
        self.write_csv(lines=feature_lines, filename='Chevrolet_Features.csv')
        self.write_csv_gallery(lines=gallery_lines, filename='Chevrolet_Gallery.csv')


class Sheet_arrange:
    def __init__(self):
        pass

    def read_csv(self, filepath):
        records = []
        with open(filepath, "r", encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                records.append(row)
        records.pop(0)
        return records

    def sort(self):
        filepath = 'C:\\Users\\USER\\Downloads\\total_count.csv'
        lines = self.read_csv(filepath=filepath)
        sheet_names = []
        import xlwt
        workbook = xlwt.Workbook()
        for col, line in enumerate(lines):
            if line[0] not in sheet_names:
                sheet_names.append(line[0])
        for sheet_name in sheet_names:
            sheet = workbook.add_sheet(sheet_name)
            sheet.write(0, 0, 'MAKE')
            sheet.write(0, 1, 'MODEL')
            sheet.write(0, 2, 'ID')
            sheet.write(0, 3, 'YEAR')
            sheet.write(0, 4, 'GALLERY')
            sheet.write(0, 5, 'PDF')
            sheet.write(0, 6, 'HOW_TO_VIDEOS')
            sheet.write(0, 7, 'FEATURES')
            col_count = 1
            for col, line in enumerate(lines):
                if sheet_name == line[0]:
                    sheet.write(col_count, 0, line[0])
                    sheet.write(col_count, 1, line[1])
                    sheet.write(col_count, 2, line[2])
                    sheet.write(col_count, 3, line[3])
                    sheet.write(col_count, 4, line[4])
                    sheet.write(col_count, 5, line[5])
                    sheet.write(col_count, 6, line[6])
                    sheet.write(col_count, 7, line[7])
                    col_count += 1
        workbook.save('Arrange.xls')


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


class Features_2020:
    def __init__(self):
        self.chevrolet = Chevrolet()

    def custome_parent(self, child):
        if child.find('picture'):
            return child
        return self.custome_parent(child.parent)

    def Nissan(self):
        # initial_url = 'https://www.nissanusa.com/'
        # initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'lxml')
        # vehicle_links = initial_soup.select('.tabs-content .vehicles-container > a')
        # collect = []
        # for vehicle_link in vehicle_links:
        #     link = 'https://nissanusa.com' + vehicle_link['href']
        #     link_soup = BeautifulSoup(requests.get(url=link).content, 'lxml')
        #     year_model = link_soup.find('p', attrs={'class': 'page-title'}).get_text().strip()
        #     year = year_model[:4]
        #     model = year_model[4:].strip()
        #     feature_link = link.replace('.html', '/features.html')
        #     print(feature_link)
        #     feature_soup = BeautifulSoup(requests.get(url=feature_link).content, 'lxml')
        #     group_headings = feature_soup.select('.heading-group')
        #     if group_headings == []:
        #         collect.append(feature_link)
        #     for group_heading in group_headings:
        #         sections_parent = group_heading.find_all_previous('div', attrs={'class': 'content-zone'})
        #         for section_parent in sections_parent:
        #             if section_parent.has_attr('id'):
        #                 section = section_parent['id']
        #                 break
        #         title = group_heading.get_text().strip()
        #         if not group_heading.parent.find('p'):
        #             continue
        #         description = group_heading.parent.find('p').get_text().strip()
        #         if not self.custome_parent(group_heading).select('img')[0].has_attr('src'):
        #             continue
        #         image = 'https://nissanusa.com' + self.custome_parent(group_heading).select('img')[0]['src']
        #         line = [year, 'Nissan', model, section, title, description, image]
        #         print(line)
        #         self.chevrolet.write_csv(lines=[line], filename='Nissan_2020.csv')
        collect = ['https://nissanusa.com/vehicles/cars/sentra/features.html',
                   'https://nissanusa.com/vehicles/electric-cars/leaf/features.html', 'https://nissanusa.com/vehicles/trucks/titan/features.html']
        for c in collect:
            year = '2020'
            model = c.split('/')[5]
            link_soup = BeautifulSoup(requests.get(url=c).content, 'html.parser')
            sliders = link_soup.select('.c_283-1_slider > a')
            for slider in sliders:
                section = slider.get_text().strip()
                slider_url = 'http://nissanusa.com' + slider['href']
                slider_soup = BeautifulSoup(requests.get(url=slider_url).content, 'lxml')
                _all = slider_soup.find_all('h3', 'c_278_tile_content_heading')
                for _a in _all:
                    title = _a.get_text().strip()
                    description = _a.find_next(text=True)

    def Dodge(self):
        initial_url = 'https://www.dodge.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html.parser')
        vehicle_links = initial_soup.select('.navigation-card-wrapper.gcss-theme-light.isImageCard.sdp-grid a')
        for vehicle_link in vehicle_links:
            if 'https://' in vehicle_link['href']:
                continue
            link = 'https://www.dodge.com' + vehicle_link['href']
            model = vehicle_link.select('span.vehicle-name.gcss-colors-text-body-primary')[0].text.strip()
            slider_soup = BeautifulSoup(requests.get(url=link).content, 'lxml')
            model_year = slider_soup.find('div', attrs={'class': 'model-details-inner'})
            if model_year:
                year = model_year.find('div', {'class': 'model-name-text'}).text[:4].strip()
                li_links = slider_soup.select('li.nav-section-link a')
                links = []
                for li_link in li_links:
                    section = li_link.get_text().strip()
                    link_url = 'https://www.dodge.com' + li_link['href']
                    if link_url not in links:
                        link_soup = BeautifulSoup(requests.get(url=link_url).content, 'html5lib')
                        brands = link_soup.find_all('h4', {'class': 'title-header'})
                        for brand in brands:
                            title = brand.text.strip()
                            description = brand.find_next('p').text.strip()
                            image = 'https://www.dodge.com' + brand.find_previous('img')['src']
                            line = [year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            print(line)
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                        blurbs = link_soup.find_all(class_='blurb-title')
                        for blurb in blurbs:
                            title = blurb.text.strip()
                            description = blurb.find_next(class_=re.compile('description'))
                            if not blurb.find_next('img'):
                                continue
                            image = 'https://www.dodge.com' + blurb.find_next('img')['src']
                            line = [year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            print(line)
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                        typegraphies = link_soup.find_all('h3', {'class': 'section-header__title gcss-typography-brand-heading-3 dodge'})
                        for typegraphy in typegraphies:
                            title = typegraphy.text.strip()
                            description = typegraphy.find_next('p').text.strip()
                            image = 'https://www.dodge.com' + typegraphy.find_next('img')['src']
                            line = [year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            print(line)
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                        boxes = link_soup.find_all('h3', 'box-title')
                        for box in boxes:
                            title = box.text.strip()
                            description = box.find_next('p').text.strip()
                            image = 'https://www.dodge.com' +  box.find_previous('img')['src']
                            line = [year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                            print(line)
                next_year = model_year.find('a').get_text().strip()
                next_link = 'https://www.dodge.com' + model_year.find('a')['href']
                next_link_soup = BeautifulSoup(requests.get(url=next_link).content, 'html5lib')
                li_links = next_link_soup.select('li.nav-section-link a')
                for li_link in li_links:
                    section = li_link.get_text().strip()
                    link_url = 'https://www.dodge.com' + li_link['href']
                    if link_url not in links:
                        link_soup = BeautifulSoup(requests.get(url=link_url).content, 'html5lib')
                        brands = link_soup.find_all('h4', {'class': 'title-header'})
                        for brand in brands:
                            title = brand.text.strip()
                            description = brand.find_next('p').text.strip()
                            image = 'https://www.dodge.com' + brand.find_previous('img')['src']
                            line = [next_year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                            print(line)
                        blurbs = link_soup.find_all(class_='blurb-title')
                        for blurb in blurbs:
                            title = blurb.text.strip()
                            description = blurb.find_next(class_=re.compile('description'))
                            if not blurb.find_next('img'):
                                continue
                            image = 'https://www.dodge.com' + blurb.find_next('img')['src']
                            line = [next_year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                            print(line)
                        typegraphies = link_soup.find_all('h3', {
                            'class': 'section-header__title gcss-typography-brand-heading-3 dodge'})
                        for typegraphy in typegraphies:
                            title = typegraphy.text.strip()
                            description = typegraphy.find_next('p').text.strip()
                            image = 'https://www.dodge.com' + typegraphy.find_next('img')['src']
                            line = [next_year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                            print(line)
                        boxes = link_soup.find_all('h3', 'box-title')
                        for box in boxes:
                            title = box.text.strip()
                            description = box.find_next('p').text.strip()
                            image = 'https://www.dodge.com' + box.find_previous('img')['src']
                            line = [next_year, 'Dodge', model, section, title, description, image]
                            if '' in line:
                                continue
                            self.chevrolet.write_csv(lines=[line], filename='Dodge_2020.csv')
                            print(line)
            else:
                print(link)
                exit()

    def Jeep(self):
        initial_url = 'https://www.jeep.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
        model_urls = initial_soup.select('.navigation-card-wrapper.gcss-theme-light.isImageCard.sdp-grid a', limit=12)
        for model_url in model_urls:
            link = 'https://www.jeep.com' + model_url['href']
            link_soup = BeautifulSoup(requests.get(url=link).text, 'html.parser')
            year_model = link_soup.find('div', {'class': 'model-details-inner'})
            year = year_model.select('.model-name-text')[0].text[:4].strip()
            model = year_model.select('.model-name-text')[0].text[4:].strip()
            section_urls = []
            section_lis = link_soup.select('li.nav-section-link a')
            for section_li in section_lis:
                if section_li in section_urls:
                    continue
                section_urls.append(section_li)
                section_link = 'https://jeep.dom' + section_li['href']
                section = section_li.get_text().strip()
                print(section_link)
                section_soup = BeautifulSoup(requests.get(url='https://www.jeep.com/wrangler.html').text, 'lxml')
                title_boxs = section_soup.find_all('h2', {'class': 'box-title'})
                for title_box in title_boxs:
                    title = title_box.get_text().strip()
                    description = title_box.parent.find('p').get_text().strip()
                    image = 'https://www.jeep.com' + self.custome_parent(title_box).find('img')['src']
                    line = [year, 'Jeep', model, section, title, description, image]
                    self.chevrolet.write_csv(lines=[line], filename='Jeep_2019_2020.csv')
            next_year = year_model.find('div', {'class': 'model-year-link'}).get_text().strip()
            next_link = 'https://www.jeep.com' + year_model.select('.model-year-link a')[0]['href']
            next_link_soup = BeautifulSoup(requests.get(url=next_link).text, 'html.parser')
            section_urls = []
            section_lis = next_link_soup.select('li.nav-section-link a')
            for section_li in section_lis:
                if section_li in section_urls:
                    continue
                section_urls.append(section_li)
                section_link = 'https://www.jeep.dom' + section_li['href']
                section = section_li.get_text().strip()
                section_soup = BeautifulSoup(requests.get(url=section_link).text, 'lxml')
                title_boxs = section_soup.find_all('h2', {'class': 'box-title'})
                for title_box in title_boxs:
                    title = title_box.get_text().strip()
                    description = title_box.parent.find('p').get_text().strip()
                    image = 'https://www.jeep.com' + self.custome_parent(title_box).find('img')['src']
                    line = [next_year, 'Jeep', model, section, title, description, image]
                    self.chevrolet.write_csv(lines=[line], filename='Jeep_2019_2020.csv')
            print(link)

    def Chrysler(self):
        initial_url = 'https://www.chrysler.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).text, 'lxml')
        vehicles = initial_soup.find_all('div', {'class': 'col-item sdp-col sdp-col-xs-6 sdp-col-sm-6 sdp-col-md-6 sdp-col-lg-3 flush'})
        for vehicle in vehicles:
            link = 'https://www.chrysler.com' + vehicle.find('a')['href']
            print(link)
            link_soup = BeautifulSoup(requests.get(url=link).text, 'lxml')
            year_model = link_soup.find('div', {'class': 'model-name-text'})
            year = year_model.get_text()[:4]
            model = year_model.get_text()[4:].strip()
            print(year, model)
            if 'pacifica' in link:
                sections_dom = link_soup.find_all('li', {'class': 'nav-section-link'})
                for i in range(len(sections_dom)//2):
                    section = sections_dom[i].get_text().strip()
                    section_link = 'https://www.chrysler.com/' + sections_dom[i].a['href']
                    section_link_soup = BeautifulSoup(requests.get(url=section_link).text, 'html.parser')
                    titles_dom = section_link_soup.select('[class*="title"]')
                    for title_dom in titles_dom:
                        title = title_dom.get_text().strip()
                        description = title_dom.find_next('p').text.strip()
                        image = 'https://www.chrysler.com' + self.custome_parent(title_dom).find('img')['src']
                        line = [year, 'Chrysler', model, section, title, description, image]
                        if '' in line or len(description) < 20:
                            continue
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Chrysler_2020.csv')
            elif '300' in link:
                sections_dom = link_soup.find_all('li', {'class': 'nav-section-link'})
                for i in range(len(sections_dom)//2):
                    section = sections_dom[i].get_text().strip()
                    section_link = 'https://www.chrysler.com' + sections_dom[i].a['href']
                    section_link_soup = BeautifulSoup(requests.get(url=section_link).content, 'lxml')
                    titles_dom = section_link_soup.select('[class*="title"]')
                    for title_dom in titles_dom:
                        title = title_dom.get_text().strip()
                        description = title_dom.find_next('p').text.strip()
                        image = 'https://www.chrysler.com' + self.custome_parent(title_dom).find('img')['src']
                        line = [year, 'Chrysler', model, section, title, description, image]
                        if '' in line or len(description) < 20:
                            continue
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Chrysler_2020.csv')
                next_year = link_soup.find('a', attrs={'data-cats-id': 'link'}).get_text().strip()
                new_link = 'https://www.chrysler.com/2020/300.html'
                new_link_soup = BeautifulSoup(requests.get(url=new_link).content, 'lxml')
                sections_dom = new_link_soup.find_all('li', {'class': 'nav-section-link'})
                for i in range(len(sections_dom) // 2):
                    section = sections_dom[i].get_text().strip()
                    section_link = 'https://www.chrysler.com' + sections_dom[i].a['href']
                    section_link_soup = BeautifulSoup(requests.get(url=section_link).content, 'lxml')
                    titles_dom = section_link_soup.select('[class*="title"]')
                    for title_dom in titles_dom:
                        title = title_dom.get_text().strip()
                        description = title_dom.find_next('p').text.strip()
                        image = 'https://www.chrysler.com' + self.custome_parent(title_dom).find('img')['src']
                        line = [next_year, 'Chrysler', model, section, title, description, image]
                        if '' in line or len(description) < 20:
                            continue
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Chrysler_2020.csv')
            titles_dom = link_soup.select('[class*="title"]')
            for title_dom in titles_dom:
                    title = title_dom.text.strip()
                    description = title_dom.find_next('p').text.strip()
                    if not title_dom.find_previous('h3', {'data-cats-id': 'section-header__title'}):
                        continue
                    section = title_dom.find_previous('h3', {'data-cats-id': 'section-header__title'}).text.strip()
                    image = 'https://www.chrysler.com' + self.custome_parent(title_dom).find('img')['src']
                    line = [year, 'Chrysler', model, section, title, description, image]
                    if '' in line or len(description) < 20:
                        continue
                    print(line)
                    self.chevrolet.write_csv(lines=[line], filename='Chrysler_2020.csv')

    def Honda(self):
        def find_parent_with_class(element):
            children = element.findChildren()
            for child in children:
                if child.has_attr('class') and child['class'] == 'category-subslide-copy':
                    return element
            if element.parent is None:
                return None
            return element.parent

        request_url = 'https://automobiles.honda.com/Honda_Automobiles/SortVehicleCards/Json/%7BF5855B0D-D2CA-4837-A7CC-ECC9DBB80F1C%7D?sortDropDownDisplayXS=False&amp;sortDropDownDisplayS=False&amp;sortDropDownDisplayM=False&amp;sortDropDownDisplayL=True&amp;sortDropDownDisplayXL=True&amp;sortIsFlyout=False'
        vehicles = requests.get(url=request_url).json()['vehicles']
        total_lines = []
        for vehicle in vehicles:
            vehicle_url = 'https://automobiles.honda.com' + vehicle['vehicleImageCTA']['url']
            vehicle_soup = BeautifulSoup(requests.get(url=vehicle_url).content, 'lxml')
            sticky_nav = vehicle_soup.select('.m_stickyNav .left-content')
            model = sticky_nav[0].find('div', {'class': 'title'}).text.strip()
            year = sticky_nav[0].select('.years ul li')
            print(vehicle_url)
            if len(year) == 2:
                previous_year = year[0].get_text().strip()
                previous_link = 'https://automobiles.honda.com' + year[0].a['href']
                previous_soup = BeautifulSoup(requests.get(url=previous_link).content, 'lxml')
                titles_dom = previous_soup.select('[class*="head"]')
                for title_dom in titles_dom:
                    category_subslide = find_parent_with_class(title_dom)
                    if category_subslide is None:
                        continue
                    if title_dom.find_previous(attrs={'class': 'blade-type'}):
                        section = title_dom.find_previous(attrs={'class': 'blade-type'}).find_next(text=True).find_next().text.strip()
                        title = title_dom.getText().strip()
                        descriptions_dom = title_dom.find_all_next(text=True)
                        for description_dom in descriptions_dom:
                            if description_dom != '\n' and description_dom.encode('utf-8').decode('utf-8').strip() != title:
                                description = description_dom.replace('\n', '').replace('\r', '').strip()
                                break
                        if self.custome_parent(title_dom).find('img').has_attr('src'):
                            image = 'https://automobiles.honda.com' + self.custome_parent(title_dom).find('img')['src'].split('?')[0]
                        elif self.custome_parent(title_dom).find('img').has_attr('srcset'):
                            image = 'https://automobiles.honda.com' + self.custome_parent(title_dom).find('img')['srcset'].split('?')[0]
                        line = [previous_year, 'Honda', model, section, title, description, image]
                        if line in total_lines:
                            continue
                        total_lines.append(line)
                        if '' in line or len(line[5]) < 20:
                            continue
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Honda_2020.csv')
                next_year = year[1].get_text().strip()
                next_link = 'https://automobiles.honda.com' + year[1].a['href']
                next_soup = BeautifulSoup(requests.get(url=next_link).content, 'lxml')
                titles_dom = next_soup.select('[class*="head"]')
                for title_dom in titles_dom:
                    category_subslide = find_parent_with_class(title_dom)
                    if category_subslide is None:
                        continue
                    if title_dom.find_previous(attrs={'class': 'blade-type'}):
                        section = title_dom.find_previous(attrs={'class': 'blade-type'}).find_next(
                            text=True).find_next().text.strip()
                        title = title_dom.getText().strip()
                        descriptions_dom = title_dom.find_all_next(text=True)
                        for description_dom in descriptions_dom:
                            if description_dom != '\n' and description_dom.encode('utf-8').decode(
                                    'utf-8').strip() != title:
                                description = description_dom.replace('\n', '').replace('\r', '').strip()
                                break
                        if self.custome_parent(title_dom).find('img').has_attr('src'):
                            image = 'https://automobiles.honda.com' + \
                                    self.custome_parent(title_dom).find('img')['src'].split('?')[0]
                        elif self.custome_parent(title_dom).find('img').has_attr('srcset'):
                            image = 'https://automobiles.honda.com' + \
                                    self.custome_parent(title_dom).find('img')['srcset'].split('?')[0]
                        line = [next_year, 'Honda', model, section, title, description, image]
                        if line in total_lines:
                            continue
                        total_lines.append(line)
                        if '' in line or len(line[5]) < 20:
                            continue
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Honda_2020.csv')
            else:
                current_year = year[0].get_text().strip()
                titles_dom = vehicle_soup.select('[class*="head"]')
                for title_dom in titles_dom:
                    category_subslide = find_parent_with_class(title_dom)
                    if category_subslide is None:
                        continue
                    if title_dom.find_previous(attrs={'class': 'blade-type'}):
                        section = title_dom.find_previous(attrs={'class': 'blade-type'}).find_next(
                            text=True).find_next().text.strip()
                        title = title_dom.getText().strip()
                        descriptions_dom = title_dom.find_all_next(text=True)
                        for description_dom in descriptions_dom:
                            if description_dom != '\n' and description_dom.encode('utf-8').decode(
                                    'utf-8').strip() != title:
                                description = description_dom.replace('\n', '').replace('\r', '').strip()
                                break
                        if self.custome_parent(title_dom).find('img').has_attr('src'):
                            image = 'https://automobiles.honda.com' + \
                                    self.custome_parent(title_dom).find('img')['src'].split('?')[0]
                        elif self.custome_parent(title_dom).find('img').has_attr('srcset'):
                            image = 'https://automobiles.honda.com' + \
                                    self.custome_parent(title_dom).find('img')['srcset'].split('?')[0]
                        line = [current_year, 'Honda', model, section, title, description, image]
                        if line in total_lines:
                            continue
                        total_lines.append(line)
                        if '' in line or len(line[5]) < 20:
                            continue
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Honda_2020.csv')

    def Lexus(self):
        initial_url = 'https://lexus.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
        vehicles = initial_soup.select('.category .stage')
        for vehicle in vehicles:
            model = vehicle.find(class_="model-name").text
            year = vehicle.find(class_="model-year").text.split(' ')[1]
            link = 'https://lexus.com' + vehicle.find('a')['href'] + '/features'
            link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
            sections_dom = link_soup.select('ul.primary-links')[1].find_all('li', {'class': 'tertiary-nav-item'})
            for section_dom in sections_dom:
                section = section_dom.get_text().strip()
                section_link = 'https://lexus.com' + section_dom.a['href']
                section_link_soup = BeautifulSoup(requests.get(url=section_link).text, 'html5lib')
                feature_items = section_link_soup.select('.feature-item')
                for feature_item in feature_items:
                    if feature_item.find('h2'):
                        title = feature_item.find('h2').text.strip()
                    else:
                        title = feature_item.find(class_=re.compile('title')).get_text().strip()
                    if feature_item.select(".description, .text, .paragraph"):
                        description = feature_item.select(".description, .text, .paragraph")[0].text.strip()
                    if not feature_item.find('img'):
                        continue
                    if feature_item.find('img').has_attr('data-original'):
                        image = 'https://lexus.com' + feature_item.find('img')['data-original']
                    elif feature_item.find('img').has_attr('data-large'):
                        image = 'https://lexus.com' + feature_item.find('img')['data-large']
                    elif feature_item.find('img').has_attr('src'):
                        image = 'https://lexus.com' + feature_item.find('img')['src']
                    else:
                        print(image)
                        exit()
                    if image == 'https://lexus.com/assets/img/global/spacer.png':
                        print(feature_item)
                        exit()
                    line = [year, 'Lexus', model, section, title, description, image]
                    print(line)
                    self.chevrolet.write_csv(lines=[line], filename='Lexus_2020.csv')

    def Kia(self):
        initial_html = """
        <ul class="list_vehicles">
                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/all-new-picanto.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_all_new_picanto1.png" alt="Picanto">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_all_new_picanto1_txt_ver2.png" class="txt" alt="Picanto" data-width="92" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_all_new_picanto1_upcoming_ver2.png" class="car" alt="Picanto">
                                        </div>
                                        <em class="name">Picanto</em>
                                    </a>
                                </li>
                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/all-new-rio-4dr.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_all_new_rio_4door1.png" alt="Rio Sedan">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_all_new_rio_4door1_txt_ver2.png" class="txt" alt="Rio Sedan" data-width="115" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_all_new_rio_4door1_upcoming_ver2.png" class="car" alt="Rio Sedan">
                                        </div>
                                        <em class="name">Rio Sedan</em>
                                    </a>
                                </li>
                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/rio.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_all_new_rio1.png" alt="Rio Hatchback">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_all_new_rio1_txt_ver2.png" class="txt" alt="Rio Hatchback" data-width="115" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_all_new_rio1_upcoming_ver2.png" class="car" alt="Rio Hatchback">
                                        </div>
                                        <em class="name">Rio Hatchback</em>
                                    </a>
                                </li>
                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/cerato-forte.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_cerato1.png" alt="Cerato/Forte">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_cerato1_txt_ver2.png" class="txt" alt="Cerato/Forte upcoming" data-width="115" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_cerato1_upcoming_ver2.png" class="car" alt="Cerato/Forte upcoming">
                                        </div>
                                        <em class="name">Cerato/Forte</em>
                                    </a>
                                </li>


                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/ceed.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_ceed1.png" alt="Ceed">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_ceed1_txt.png" class="txt" alt="Ceed upcoming2" data-width="94" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_ceed1_upcoming.png" class="car" alt="Ceed upcoming2">
                                        </div>
                                        <em class="name">Ceed</em>
                                    </a>
                                </li>

                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/proceed.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_pro-ceed1.png" alt="ProCeed">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_pro-ceed1_txt.png" class="txt" alt="ProCeed upcoming2" data-width="142" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_pro-ceed1_upcoming.png" class="car" alt="ProCeed upcoming2">
                                        </div>
                                        <em class="name">ProCeed</em>
                                    </a>
                                </li>


                                <!-- <li data-group="group2">
                                    <a href="/worldwide/vehicles/ceed.do">
                                        <img src="/worldwide/images/vehicles/img_ceed1.png" alt="cee’d" />
                                        <em class="name">cee’d</em>
                                    </a>
                                </li>
                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/ceed-3dr.do">
                                        <img src="/worldwide/images/vehicles/img_pro-ceed1.png" alt="pro_cee’d" />
                                        <em class="name">pro_cee’d</em>
                                    </a>
                                </li> -->

                                <!-- <li data-group="group2">
                                    <a href="/worldwide/vehicles/ceed-sportswagon.do">
                                        <img src="/worldwide/images/vehicles/img_ceed-sw-sp1.png" alt="cee’d Sportswagon" />
                                        <em class="name">cee’d Sportswagon</em>
                                    </a>
                                </li> -->

                                <li data-group="group2"> <!-- 20190403 group2로 수정 -->
                                    <a href="/worldwide/vehicles/optima.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_optima1.png" alt="Optima">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_optima1_txt.png" class="txt" alt="Optima upcoming2" data-width="115" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_optima1_upcoming.png" class="car" alt="Optima upcoming2">
                                        </div>
                                        <em class="name">Optima</em>
                                    </a>
                                </li>

                                <!-- <li data-group="group4">
                                    <a href="/worldwide/vehicles/all-new-optima-hybrid.do">
                                        <img src="/worldwide/images/vehicles/img_all_new_optima_hybrid1.png" alt="Optima Hybrid" />
                                        <em class="name">Optima Hybrid</em>
                                    </a>
                                </li> -->
                                <li data-group="group4"> <!-- 20190403 group4로 수정 -->
                                    <a href="/worldwide/vehicles/optima-hybrid.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_optima_hybrid1.png" alt="Optima Hybrid">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_optima_hybrid1_txt.png" class="txt" alt="Optima Hybrid upcoming2" data-width="138" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_optima_hybrid_upcoming.png" class="car" alt="Optima Hybrid upcoming2">
                                        </div>
                                        <em class="name">Optima Hybrid</em>
                                    </a>
                                </li>



                                <!--  <li data-group="group2">
                                    <a href="/worldwide/vehicles/all-new-cadenza.do">
                                        <img src="/worldwide/images/vehicles/img_all_new_cadenza1.png" alt="Cadenza" />
                                        <em class="name">Cadenza</em>
                                    </a>
                                </li> -->
                                <!-- s:20191217 -->
                                <li data-group="group2" class="new">
                                    <a href="/worldwide/vehicles/cadenza.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_cadenza.png" alt="Cadenza">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_cadenza_txt.png" class="txt" alt="Cadenza upcoming2" data-width="138" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_cadenza_upcoming.png" class="car" alt="Cadenza upcoming2">
                                        </div>
                                        <em class="name">Cadenza</em>
                                    </a>
                                </li>
                                <!-- e:20191217 -->

                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/stinger.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_Stinger1.png" alt="Stinger">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_stinger1_txt_ver2.png" class="txt" alt="Stinger upcoming" data-width="150" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_Stinger1_upcoming_ver2.png" class="car" alt="Stinger upcoming">
                                        </div>
                                        <em class="name">Stinger</em>
                                    </a>
                                </li>
                                <li data-group="group2">
                                    <a href="/worldwide/vehicles/k900.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_K900.png" alt="K900">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_K900_txt_ver2.png" class="txt" alt="K900" data-width="150" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_K900_upcoming_ver2.png" class="car" alt="K900">
                                        </div>
                                        <em class="name">K900</em>
                                    </a>
                                </li>

                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/stonic.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_stonic1.png" alt="stonic">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_stonic1_txt_ver2.png" class="txt" alt="stonic" data-width="150" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_stonic1_upcoming_ver2.png" class="car" alt="stonic">
                                        </div>
                                        <em class="name">Stonic</em>
                                    </a>
                                </li>
                                <!--  <li data-group="group4">
                                    <a href="/worldwide/vehicles/niro.do">
                                        <img src="/worldwide/images/vehicles/img_niro1.png" alt="Niro" />
                                        <em class="name">Niro</em>
                                    </a>
                                </li> -->
                                
                                <!-- s:20191118 eidt & add -->
                  <li data-group="group4" class="new">
                     <a href="/worldwide/vehicles/niro.do" class="upcoming2" style="background:none;">
                     <img src="/worldwide/images/vehicles/img_niro_201911.png" alt="Niro">
                     <div class="animate" style="display: none; opacity: 0; width: 0px; left: 50%;">
                      <img src="/worldwide/images/vehicles/img_niro_201911_txt.png" class="txt" alt="Niro" data-width="138" data-height="47" style="top: 56px; left: 26.5px; width: 138px;">
                      <img src="/worldwide/images/vehicles/img_niro_201911_2.png" class="car" alt="Niro" style="display: none;">
                     </div>
                     <em class="name">Niro<br>(Hybrid, Plug-in Hybrid)</em>
                     </a>
                  </li>
                  <li data-group="group4" class="new">
                     <a href="/worldwide/vehicles/e-niro.do" class="upcoming2" style="background:none;">
                     <img src="/worldwide/images/vehicles/img_e-niro_201911.png" alt="Niro">
                     <div class="animate" style="display: none; opacity: 0; width: 0px; left: 50%;">
                      <img src="/worldwide/images/vehicles/img_e-niro_201911_txt.png" class="txt" alt="e-Niro" data-width="138" data-height="47" style="top: 56px; left: 26.5px; width: 138px;">
                      <img src="/worldwide/images/vehicles/img_e-niro_201911_2.png" class="car" alt="e-Niro" style="display: none;">
                     </div>
                     <em class="name">e-Niro</em>
                     </a>
                  </li>
                  <!-- e:20191118 -->
                                

                <!-- 20190326 new soul -->
                <li data-group="group3" class="new">
                    <a href="/worldwide/vehicles/soul.do" class="upcoming2" style="background:none;">
                        <img src="/worldwide/images/vehicles/img_soul_201903_1.png" alt="Soul">
                        <div class="animate">
                            <img src="/worldwide/images/vehicles/img_soul_201903_txt.png" class="txt" alt="Soul" data-width="138" data-height="47">
                            <img src="/worldwide/images/vehicles/img_soul_201903_2.png" class="car" alt="Soul">
                        </div>
                        <em class="name">Soul</em>
                    </a>
                </li>
                <!-- //20190326 -->

                <!-- 2019026 기존 soul 메뉴 삭제
                                <li data-group="group3" class="new">
                                    <a href="/worldwide/vehicles/all-new-soul.do" class="upcoming2">
                                        <img src="/worldwide/images/vehicles/img_all_new_soul1.png" alt="Soul">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_all_new_soul1_txt.png" class="txt" alt="Soul upcoming" data-width="138" data-height="47" />
                                            <img src="/worldwide/images/vehicles/img_all_new_soul_upcoming.png" class="car" alt="Soul upcoming" />
                                        </div>
                                        <em class="name">Soul</em>
                                    </a>
                                </li>

                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/soul.do">
                                        <img src="/worldwide/images/vehicles/img_soul1.png" alt="Soul" />
                                        <em class="name">Soul</em>
                                    </a>
                                </li>
                -->

                                
                                
                                <!-- 20190802 add -->
                                <li data-group="group4" class="new">
                                  <a href="/worldwide/vehicles/e-soul.do" class="upcoming2" style="background:none;">
                                    <img src="/worldwide/images/vehicles/img_soul1_ev.png" alt="e-Soul">
                                    <div class="animate">
                                      <img src="/worldwide/images/vehicles/img_soul1_txt.png" class="txt" alt="e-Soul" data-width="138" data-height="47">
                                      <img src="/worldwide/images/vehicles/img_soul1_upcoming.png" class="car" alt="e-Soul">
                                    </div>
                                    <em class="name">e-Soul</em>
                                  </a>
                                </li>
                                <!-- // 20190802 add -->
                                
                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/carens-rondo.do">
                                        <img src="/worldwide/images/vehicles/img_carens-rondo1.png" alt="Carens/Rondo">
                                        <em class="name">Carens/Rondo</em>
                                    </a>
                                </li>
                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/carnival.do">
                                        <img src="/worldwide/images/vehicles/img_carnival1.png" alt="Grand Carnival/Sedona">
                                        <em class="name">Grand Carnival/Sedona</em>
                                    </a>
                                </li>

                                <!--

                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/all-new-sportage.do">
                                        <img src="/worldwide/images/vehicles/img_new_sportage1.png" alt="Sportage" />
                                        <em class="name">Sportage</em>
                                    </a>
                                </li>
                                -->
                                <li data-group="group3" class="new">
                                    <a href="/worldwide/vehicles/sportage.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_sportage1.png" alt="Sportage">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_sportage1_txt.png" class="txt" alt="Sportage" data-width="138" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_sportage1_upcoming.png" class="car" alt="Sportage">
                                        </div>
                                        <em class="name">Sportage</em>
                                    </a>
                                </li>



                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/sorento.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_sorento1.png" alt="Sorento">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_sorento1_txt_ver2.png" class="txt" alt="Sorento" data-width="150" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_sorento1_upcoming_ver2.png" class="car" alt="Sorento">
                                        </div>
                                        <em class="name">Sorento</em>
                                    </a>
                                </li>

                                <li data-group="group3">
                                    <a href="/worldwide/vehicles/mohave.do">
                                        <img src="/worldwide/images/vehicles/img_mohave1.png" alt="Mohave">
                                        <em class="name">Mohave</em>
                                    </a>
                                </li>
                                <!--190514 add-->
                                <li data-group="group3" class="new">
                                  <a href="/worldwide/vehicles/telluride.do">
                                    <img src="/worldwide/images/vehicles/img_telluride1.png" alt="Telluride">
                                    <em class="name">Telluride</em>
                                  </a>
                                </li>
                                <!--//190514 add-->
                                 <!-- s:20190603 -->
                                <!--  
                                <li data-group="group3" class="new">
                                  <a href="/worldwide/vehicles/unveiling-seltos.do" class="upcoming2">
                                    <img src="/worldwide/images/vehicles/img_seltos.png" width="160" alt="Seltos">
                                    <em class="name">Seltos</em>
                                  </a>
                                </li>
                                -->
                                 
                                
                                  <!-- s:20191202 edit -->
                                   
                                <li data-group="group3" class="new">
                                    <a href="/worldwide/vehicles/seltos.do" class="upcoming2" style="background:none;">
                                        <img src="/worldwide/images/vehicles/img_seltos_19120.png" alt="Seltos">
                                        <div class="animate">
                                            <img src="/worldwide/images/vehicles/img_seltos_txt.png" class="txt" alt="Seltos" data-width="150" data-height="47">
                                            <img src="/worldwide/images/vehicles/img_seltos_191202_2.png" class="car" alt="Seltos">
                                        </div>
                                        <em class="name">Seltos</em>
                                    </a>
                                </li>
                                
                                 <!-- e:20191202 edit -->
                                 
                                <!-- e:20190603 -->
                                <li data-group="group5">
                                    <a href="/worldwide/vehicles/k2500-k2700-k3000s-k4000g.do">
                                        <img src="/worldwide/images/vehicles/img_k2700-k2500-k4000g1.png" alt="K2500/K2700/K3000S/K4000G">
                                        <em class="name">K2500/K2700/<br>K3000S/K4000G</em>
                                    </a>
                                </li>
                            </ul>"""
        initial_soup = BeautifulSoup(initial_html, 'html5lib')
        vehicles = initial_soup.select('ul.list_vehicles li')
        for vehicle in vehicles:
            model = vehicle.get_text().strip()
            vehicle_link = 'https://www.kia.com' + vehicle.a['href']
            vehicle_link_soup = BeautifulSoup(requests.get(url=vehicle_link).content, 'html5lib')
            special_bar = vehicle_link_soup.find(attrs={'class': 'evt_specialMn'})
            if special_bar:
                print(vehicle_link)
                content = vehicle_link_soup.find(id="content")
                content_divs = content.find_all('div', recursive=False)
                for content_div in content_divs:
                    section = content_div['class'][0]
                    cents = content_div.find_all('[class*="cont"]')
                    if cents:
                        for cont in cents:
                            if cont.has_attr('class') and 'cont' in content_div['class']:
                                title = content_div.find(class_='txt').get_text().strip()
                                description = content_div.select('[class*="sTxt"]')[0].get_text().strip()
                                image = 'https://www.kia.com' + content_div.find(class_='photo').img['src']
                                line = ['2020', 'Kia', model, section, title, description, image]
                                print(line)
                    else:
                        for cent in cents:
                            print(cent)
                            exit()
                            if cent.find(class_='txt'):
                                title = content_div.find(class_='txt').get_text().strip()
                            else:
                                title = ''
                            if cent.find_all('[class*="sTxt"]'):
                                description = content_div.select('[class*="sTxt"]')[0].get_text().strip()
                            else:
                                description = ''
                            if cent.find('img'):
                                image = 'https://www.kia.com' + content_div.find('img')['src']
                            else:
                                image = ''
                            line = ['2020', 'Kia', model, section, title, description, image]
                            print(line)
            else:
                items = vehicle_link_soup.select('.slider_contain .item')
                print(vehicle_link)
                for item in items:
                    if item.find_previous(class_='tit_section'):
                        section = item.find_previous(class_='tit_section').getText().strip()
                    else:
                        continue
                        # section = item.find_previous(class_='tit').getText().strip()
                    title = item.select('.description')[0].find(class_='tit').get_text().strip()
                    if item.select('.description')[0].find(class_='desc'):
                        description = item.select('.description')[0].find(class_='desc').get_text().strip()
                    else:
                        description = ''
                    image = 'https://www.kia.com' + item.find('img')['src']
                    line = ['2020', 'Kia', model, section, title, description, image]
                    print(line)
                    self.chevrolet.write_csv(lines=[line], filename='Kia_2020.csv')

    def Hyundai(self):
        initial_url = 'https://www.hyundaiusa.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
        vehicles = initial_soup.select('#vehicles .model')
        for vehicle in vehicles:
            if vehicle.find('div', {'class': 'model-name'}):
                year_model = vehicle.find('div', {'class': 'model-name'}).get_text()
                year = year_model[:4]
                model = year_model[4:].strip()
                model_link = 'https://www.hyundaiusa.com' + vehicle.a['href']
                if model_link == 'https://www.hyundaiusa.com/veloster-n/index.aspx':
                    model_link = 'https://www.hyundaiusa.com/veloster/index.aspx'
                model_link_soup = BeautifulSoup(requests.get(url=model_link).content, 'html5lib')
                copies = model_link_soup.find_all('div', attrs={'class': 'copy'})
                print(model_link)
                tmp_title = ''
                for copy in copies:
                    if not copy.find_parent('section'):
                        continue
                    if copy.parent.find('div', {'class': 'subhead'}):
                        section = copy.find_previous('div', {'class': 'headline'}).text.strip()
                        title = copy.find_previous('div', {'class': 'subhead'}).text.strip()
                        if tmp_title == title:
                            continue
                        description = copy.text.strip()
                    else:
                        if not copy.find_parent('section').find('div', {'class': 'headline'}):
                            continue
                        section = copy.find_parent('section').find('div', {'class': 'headline'}).text.strip()
                        title = copy.find_previous('div', {'class': 'headline'}).text.strip()
                        if title == tmp_title:
                            continue
                        description = copy.text.strip()
                    if self.custome_parent(copy).find('img').has_attr('src'):
                        image = 'https://www.hyundaiusa.com' + self.custome_parent(copy).find('img')['src']
                    elif self.custome_parent(copy).find('img').has_attr('data-lazy'):
                        image = self.custome_parent(copy).find('img')['data-lazy']
                    else:
                        print(self.custome_parent(copy).find('img'))
                        exit()
                    tmp_title = title
                    line = [year, 'Hyundai', model, section, title, description, image]
                    if '' in line:
                        continue
                    print(line)
                    self.chevrolet.write_csv(lines=[line], filename='Hyundai_2020.csv')

    def Infiniti(self):
        initial_url = 'https://www.infinitiusa.com/vehicles/new-vehicles.html'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser')
        vehicles = initial_soup.find_all('h3', {'class': 'car-title'})
        for vehicle in vehicles:
            year = vehicle.text[:5].strip()
            model = vehicle.text[5:].strip()
            link = 'https://www.infinitiusa.com' + vehicle.a['href'].replace('.html', '/features.html')
            link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
            content_group = link_soup.find_all('div', class_='content-group')
            if link == 'https://www.infinitiusa.com/vehicles/crossovers/qx60/features.html':
                soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
                centers = soup.select('[class^=c_00]')
                for center in centers:
                    if not center.find('div', {'class': 'heading-group'}):
                        continue
                    title = center.find('div', {'class': 'heading-group'}).text.strip()
                    if not center.select('div p'):
                        continue
                    descriptions_dom = center.find_all('p')
                    for description_dom in descriptions_dom:
                        if not description_dom.has_attr('class'):
                            description = description_dom.text.strip()
                    image = 'https://www.infiniti.com' + center.find_previous('img')['src']
                    section = center.find_previous('div', {'class': 'c_004'}).text.strip()
                    line = [year, 'Infiniti', model, section, title.replace('\n', '').replace('  ', ''), description, image]
                    print(line)
                    self.chevrolet.write_csv(lines=[line], filename='Infiniti_2020.csv')
                continue
            if content_group:
                print(link)
                if link == 'https://www.infinitiusa.com/vehicles/coupes/q60/features.html':
                    lines = [
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', 'TURBO ENGINES ACCELERATE YOUR POTENTIAL AND PERFORMANCE', 'This is power through innovation, where the forces of advanced technology blow past limits. Two turbocharged V6 powertrain variants culminate in jaw-dropping performance.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/2020-infiniti-q60-coupe-engine.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', 'INVENTIVE IN MOTION IT’S NOT JUST A CAR, IT’S AN EXPERIENCE', 'A 3.0-liter V6 twin-turbo engine that can put up to 300 horsepower on the road. INFINITI cutting-edge technologies put you in position to manage your performance, with more power when you need it most.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/2020-infiniti-q60-red-sport-400-luxury-coupe.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', '300-HP 3.0-LITER V6 TWIN-TURBO ENGINE', 'Tap into 300 horsepower and 295 pound-feet of torque, quicker than you ever imagined. A variant of the V6, it propels you beyond measure, courtesy of a lightweight aluminum engine, friction-reducing technologies, plus cooling and valve timing systems.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/infiniti-q60-turbo-engine.jpg.ximg.l_6_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', '400-HP 3.0-LITER V6 TWIN-TURBO ENGINE', 'Standard on the Q60 RED SPORT 400, the V6 twin-turbo’s 350 pound-feet of torque builds quickly and power pours out like an endless flood. Acceleration is instant and feels limitless. Direct Injection Gasoline, water-cooled air charging, a turbo speed sensor and advanced turbine blade design make for quicker response and a higher peak.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/infiniti-q60-turbo-engine.jpg.ximg.l_6_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', 'DYNAMIC DIGITAL SUSPENSION HANDLE WITH INSTANT ADAPTABILITY', 'The Q60’s available Dynamic Digital Suspension can adjust continually to corners and road imperfections, striking an ideal balance between performance and cushioning for something revolutionary. Drivers can also take control with the flick of a switch, manually switching from the comfort-bias to a sportier ride, highly responsive and personal to heighten your driving experience', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/2020-infiniti-q60-coupe-dynamic-digital-suspension.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', 'DIRECT ADAPTIVE STEERING® IT PUTS THE FUTURE OF DRIVING IN YOUR HANDS', 'After many years of research and development, Q60’s optional Second-generation Direct Adaptive Steering® is here to revolutionize how we drive. This system digitally and instantaneously transmits your steering input directly to the wheels. Its digital processing power lets you steer quicker and smoother than you ever imagined. When you are driving on rough or uneven roads, the system is constantly, automatically making subtle adjustments to give you an increased feeling of stability, while decreasing vibration through the steering wheel.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/2020-infiniti-q60-digital-dynamic-suspension.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'PERFORMANCE', 'DRIVE MODE SELECTOR CHOOSE YOUR DRIVE', 'INFINITI Drive Mode Selector takes performance and control to a more refined level. Select between Standard, Snow, available ECO, Sport, available Sport+, and Personal modes. Then further tailor your drive by tuning steering, engine and suspension inputs. The result is one that suits the moment and more importantly, can be personalized exactly to your liking. Expand your experience beyond road conditions and preset factory settings.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/infiniti-q60-coupe-drive-mode-selector.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'DESIGN', 'UNIQUE DESIGN DESIGN THAT KNOWS NO BOUNDS', "Daring curves, deep creases, and flowing lines intensify Q60's low, wide, powerful stance. Signature elements like eye-inspired headlights and a double-arch grille make it unmistakably INFINITI. Progressive and modern, yet dynamic and moving, this is a new kind of sports coupe.", 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/red-2020-infiniti-q60-coupe-grille.jpg.ximg.l_full_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'DESIGN', 'WIDE POWERFUL STANCE AN ELEVATED DESIGN EXPRESSION', 'The dynamic proportions make a purpose-built statement. Low enough to stick to the ground. Wide enough to deliver greater stability. With a low hood height for an unobstructed view of the road so you truly feel connected to everything around you.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/design/2020-infiniti-q60-coupe-dynamic-sunstone-red.jpg.ximg.l_4_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'DESIGN', 'EXPRESSIVE ILLUMINATION SEE FARTHER', 'Eye-inspired LED headlights give a provocative stare that can be seen from both the front and side. The optional Adaptive Front lighting System turns the headlights as you turn the steering wheel, improving visibility at intersections and around curves.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/performance/2020-infiniti-q60-coupe-headlamps.jpg.ximg.l_4_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'DESIGN', 'ZERO LIFT FRONT AND REAR AERODYNAMICS STABILITY AT HIGH SPEEDS', "Q60 features a front and rear “Zero Lift” aerodynamic design that helps keep the vehicle stable at high speeds, helping to mitigate unforeseen aerodynamic effects to the vehicle's path. It also helps keep the vehicle more stable in cross-wind situations.", 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/design/infiniti-q60-coupe-aerodynamic-illustration.jpg.ximg.l_4_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design Ultramodern Style', 'Dramatic Graphite Leatherette is sharply contrasted with a Brushed Aluminum trim. Shown for 2020 Q60 3.0t PURE/PURE AWD.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-graphite-leatherette-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design ULTRAMODERN STYLE', 'Dramatic Graphite Leatherette is sharply contrasted with a Brushed Aluminum trim. Shown for 2020 Q60 3.0t LUXE/LUXE AWD.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-graphite-leatherette-aluminum-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'THE ELEMENTS OF DESIGN TRADITIONAL CRAFTSMANSHIP, MODERN MATERIALS', 'Dramatic Graphite Semi-Aniline Leather-appointed seating is sharply contrasted with a Brushed Aluminum trim. Shown for 2020 Q60 3.0t LUXE/LUXE AWD. **Requires additional package on all models', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-semi-aniline-leather-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design A SUBTLE PAIRING', 'The muted elegance of Stone Leatherette is accented by Brushed Aluminum trim. This interior design is available on: Q60 3.0t LUXE and Q60 3.0t LUXE AWD.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-stone-leatherette-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design A TAILORED APPROACH', 'Our striking Gallery White Semi-Aniline Leather-appointed seating is complemented by Brushed Aluminum trim throughout. This interior design is available on: Q60 3.0t LUXE and Q60 3.0t LUXE AWD. **Requires additional package on all models', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-white-semi-aniline-leather-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design Sleek and Contemporary', 'Dramatic Graphite Semi-Aniline Leather-appointed seating is sharply contrasted with Carbon Fiber trim. Shown for 2020 Q60 RED SPORT 400/RED SPORT 400 AWD. **Requires additional package on all models', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-graphite-semi-aniline-leather-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design A TAILORED APPROACH', 'The distinctive Gallery White Semi-Aniline Leather-appointed seating and Black Carbon Fiber trim combine for a crisp, clean interior style. This interior design combination is exclusive to: Q60 RED SPORT 400 and Q60 RED SPORT 400 AWD. **Requires additional package on all models', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-white-leather-red-accent-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'The Elements of Design A BOLD CHOICE', 'Vivid Monaco Red Semi-Aniline Leather-appointed seating is matched with Black Carbon Fiber trim for a contemporary interior style. This red sport interior design is exclusive to: Q60 RED SPORT 400 and Q60 RED SPORT 400 AWD. **Requires additional package on all models', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-monaco-red-leather-interior.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'Matchless Materials A Body Of Art Crafted Expressly For You', 'Tailored to complement the human form, the cabin celebrates the driver with bold thinking and fine modern materials. The moment you enter, you will understand what true craftsmanship is. You can choose between available accents like Brushed Aluminum trim or Black Carbon Fiber trim.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-q60-interior-leather-seats-cup-holders.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'UNIQUE STITCHING Tailored And Accented', 'Craftsmanship is obvious with tighter stitching and more dynamic free-flowing shapes.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-q60-interior-door-panel-red-stitching-window-controls.jpg.ximg.l_4_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'SPORT SEAT DESIGN Exquisite Comfort', "Crafted to blend comfort with science, the design of the driver's seat allows you to perform at a higher level. Feel the sport-inspired difference. Deep bolsters and an integrated headrest hold you securely in place, while spinal support research led to a luxuriously comfortable design that can help reduce fatigue on long drives.", 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/2020-infiniti-q60-coupe-interior-monaco-red-leather.jpg.ximg.l_4_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'SPORT STEERING WHEEL Natural Grip', 'Your hands move in unique ways and a steering wheel should reflect that. This one does. Sport-inspired thumb grips and paddle shifters are just the right shape for performance driving.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/infiniti-q60-red-sport-400-steering-wheel.jpg.jpg.ximg.l_4_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'INTERIOR', 'Bose® Performance Series Audio You Can Hear It Here First', 'Bose® Performance Series Audio System includes 13 speakers, Advanced Staging Technology, Centerpoint® 2.0 Surround, AudioPilot® 2.0 Noise Compensation, multiple 10-inch and 6 x 9-inch woofers and a lightweight silk dome tweeter. This system features genuine aluminum speaker grilles that offer a touch of style and craftsmanship to the interior. You’ll experience true concert-like sound through speakers that create a wider soundstage.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/interior/infiniti-q60-coupe-bose-audio.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'APPLE CARPLAY®', 'Apple CarPlay® is the safer, smarter way to enjoy the things you love on your compatible iPhone while driving. Access Apple Music, Apple Maps, make calls, send and receive messages – all hands-free. Just plug in your iPhone and go.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/technology/2020-infiniti-q60-interior-intouch-apple-carplay.jpg.ximg.l_full_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'PREDICTIVE FORWARD COLLISION WARNING MONITOR YOUR SURROUNDINGS', "Predictive Forward Collision Warning can alert the driver of risks that may be obscured from the driver's forward field-of-view. It senses the relative velocity and distance of a vehicle traveling in front of the car right ahead.", 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/technology/infiniti-q60-predictive-forward-collision-warning.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'LANE DEPARTURE PREVENTION AND ACTIVE LANE CONTROL MAINTAIN YOUR LANE', 'Available Lane Departure Warning and Lane Departure Prevention systems can help warn the driver if they start to drift out of their lane and can even intervene if necessary. Active Lane Control monitors lane markers and evaluates the road conditions, while making fine adjustments to your steering.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/technology/infiniti-q60-lane-departure-prevention-active-lane-control.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'AROUND VIEW® MONITOR WITH MOVING OBJECT DETECTION HEIGHTENED AWARENESS', "The available Around View® Monitor delivers advanced yet intuitive technology, helping to make parking easier. Four cameras positioned around the vehicle give you a virtual 360° bird's-eye view on your display. This INFINITI system is enhanced with Moving Object Detection — alerting you to moving objects detected within the display image. Offering a new perspective of the world around you, your INFINITI helps you navigate even the tightest spaces.", 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/technology/infiniti-q60-around-view-monitor.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'BLIND SPOT WARNING AND BLIND SPOT INTERVENTION® SAFETY BEYOND WHAT YOU SEE', 'INFINITI’s available Blind Spot Warning System can help alert the driver to vehicles detected in the blind spot area. An indicator light illuminates if the presence of another vehicle is detected in the blind spot area. If the driver engages the turn signal, the indicator flashes and an audible warning sounds. And with the available Blind Spot Intervention®, if your Q60 begins to merge into a lane with another vehicle, the system will automatically help keep you in your lane.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/technology/infiniti-q60-blind-spot-warning-intervention.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'OWNER BENEFITS', 'TOTAL OWNERSHIP EXPERIENCE® COMMITTED TO YOU', 'At INFINITI, we are committed to making every aspect of ownership rewarding. We honor this commitment with personalized service that anticipates, recognizes, and understands your individual needs. We stand behind it with a comprehensive program of premium services and coverage to help ensure your satisfaction.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/owner-benefits/2020-infiniti-q60-red-sport-coupe-dynamic-sunstone-red.jpg.ximg.l_full_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'PREMIUM SERVICES COMPREHENSIVE SUPPORT', 'A defining quality of the INFINITI Total Ownership Experience® is the way we support you with premium services:', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/owner-benefits/2020-infiniti-q60-exterior-driver-side.jpg.ximg.l_12_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'FINANCIAL FLEXIBILITY CONVENIENT, CUSTOM PLANS', 'A commitment to meeting all of your personal needs is never more evident than with INFINITI Financial Services. INFINITI Financial Services offers creative lease and purchase options with convenient payment plans that are tailored to your needs. Visit the Financing section for more detailed information.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/owner-benefits/2020-infiniti-q60-interior-graphite-leather-wrapped-steering-wheel.jpg.ximg.l_6_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'HIGH PERFORMANCE IN A CREDIT CARD', 'Apply for an INFINITI® Visa® Card today.', 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Owner%20Benefits/infiniti-owner-benefits-visa-credit-card.jpg.ximg.l_6_m.smart.jpg'],
                        ['2020', 'Infiniti', 'Q60', 'TECHNOLOGY', 'INFINITI WARRANTY PROTECTION AN EXTRA MEASURE OF REASSURANCE', "Every new INFINITI comes with the peace of mind of the INFINITI New Vehicle Limited Warranty, including 6-year/70,000-mile powertrain and 4-year/60,000-mile (whichever occurs first) basic coverage. Or purchase the INFINITI Elite Extended Protection Plan for additional protection for covered components for up to 8 years or 120,000 miles and extends your 4-year Roadside Assistance. Visit the Ownership section for more detailed warranty information. For complete information concerning coverage, conditions and exclusions, see your INFINITI retailer and read the actual New Vehicle Limited Warranty booklet.", 'https://www.infinitiusa.com/content/dam/Infiniti/US/vehicles/Q60/MY20/features/owner-benefits/2020-infiniti-q60-red-sport-400-exterior.jpg.ximg.l_12_m.smart.jpg'],
                    ]
                    self.chevrolet.write_csv(lines=lines, filename='Infiniti_2020.csv')
                for content in content_group:
                    try:
                        title = content.find_all('p')[1].b.get_text().strip()
                        content.find_all('p')[1].b.decompose()
                        description = content.find_all('p')[1].get_text().strip()
                        image = 'https://www.infinitiusa.com' + content.find_previous('picture').img['src']
                        section = content.find_previous('h2', {'class': 'heading'}).text.strip()
                        line = [year, 'Infiniti', section, title, description, image]
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Infiniti_2020.csv')
                    except:
                        continue
            else:
                print(link)
                heli_sections = link_soup.find_all('div', class_='heliostext section')
                for heli_section in heli_sections:
                    if not heli_section.find(class_='heading-group'):
                        continue
                    title = heli_section.find(class_='heading-group').get_text().strip()
                    heli_section.find(class_='heading-group').decompose()
                    if heli_section.find('ul'):
                        heli_section.find('ul').decompose()
                    description = heli_section.text.strip()
                    image = 'https://www.infinitiusa.com' + heli_section.find_previous('picture').img['src']
                    section = heli_section.find_previous('div', {'class': 'c_004'}).text.strip()
                    line = [year, 'Infiniti', model, section.replace('\n', '').replace('  ', ''), title.replace('\n', '').replace('  ', ''), description.strip(), image]
                    print(line)
                    self.chevrolet.write_csv(lines=[line], filename='Infiniti_2020.csv')

    def Ford(self):
        initial_url = 'https://www.ford.com/'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
        vehicles = initial_soup.select('.tertiary_menu.nav.navbar-nav.vehicles > li')
        for i in range(len(vehicles)//2):
            vehicle = vehicles[i]
            year = vehicle.find('span', class_='year').text[:4].strip()
            model = vehicle.find('span', class_='year').text[4:].strip()
            link = 'https://www.ford.com' + vehicle.a['href'].strip()
            link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
            if link_soup.select('ul.dropdown.subnav.subnav-wrapper li:nth-child(3) a'):
                feature_link = 'https://www.ford.com' + link_soup.select('ul.dropdown.subnav.subnav-wrapper li:nth-child(3) a')[0]['href']
                feature_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
                feature_titles = feature_soup.select('.featuresTile.fi-startcard > a')
                for feature_title in feature_titles:
                    section = feature_title.find(class_='fi-category-name').text.strip()
                    feature_url = 'https://www.ford.com' + feature_title['href']
                    feature_url_soup = BeautifulSoup(requests.get(url=feature_url).content, 'html5lib')
                    brands = feature_url_soup.select('[class*="fgx-brand-exlt-h2"]')
                    print(feature_url)
                    for brand in brands:
                        title = brand.text.strip()
                        description = brand.find_next('span', class_='description').text.strip()
                        image = 'https://www.ford.com' + self.custome_parent(brand.parent).find('img')['src']
                        line = [year, 'Ford', model, section, title, description, image]
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Ford_2020.csv')
                    add_brands = feature_url_soup.select('[class*="fgx-brand-lt-h4"]')
                    for add_brand in add_brands:
                        title = add_brand.text.strip()
                        description = brand.find_next('span', class_='description').text.strip()
                        image = 'https://www.ford.com' + self.custome_parent(brand.parent).find('img')['src']
                        line = [year, 'Ford', model, section, title, description, image]
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Ford_2020.csv')

    def Cadillac(self):
        def find_parent_under_body(ele):
            if ele.parent.name == 'body':
                return ele
            return ele.parent
        lines = []
        links = ['http://www.cadillac.com/suvs/xt4', 'http://www.cadillac.com/suvs/xt5', 'http://www.cadillac.com/suvs/xt6', 'http://www.cadillac.com/suvs/escalade', 'http://www.cadillac.com/future-vehicles/escalade-suv', 'http://www.cadillac.com/sedans/ct4', 'https://www.cadillac.com/sedans/ct4#ct4-v', 'http://www.cadillac.com/sedans/ct5', 'https://www.cadillac.com/sedans/ct5#ct5-v', 'http://www.cadillac.com/sedans/cts-sedan', 'http://www.cadillac.com/sedans/xts-sedan', 'http://www.cadillac.com/sedans/ct6', 'http://www.cadillac.com/sedans/ct6-v', 'http://www.cadillac.com/suvs/xt4', 'http://www.cadillac.com/suvs/xt5', 'http://www.cadillac.com/suvs/xt6', 'http://www.cadillac.com/suvs/escalade', 'http://www.cadillac.com/future-vehicles/escalade-suv', 'http://www.cadillac.com/sedans/ct4', 'https://www.cadillac.com/sedans/ct4#ct4-v', 'http://www.cadillac.com/sedans/ct5', 'https://www.cadillac.com/sedans/ct5#ct5-v', 'http://www.cadillac.com/sedans/cts-sedan', 'http://www.cadillac.com/sedans/xts-sedan', 'http://www.cadillac.com/sedans/ct6', 'http://www.cadillac.com/sedans/ct6-v', 'https://www.cadillac.com/sedans/ct4#ct4-v', 'https://www.cadillac.com/sedans/ct5#ct5-v', 'http://www.cadillac.com/sedans/ct6-v']
        for link in links:
            link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
            model = link_soup.select('#nav_anchor > span')[0].text.strip()
            year_toggle_lis = link_soup.select('.q-year-toggle-list li')
            if len(year_toggle_lis) == 2:
                for year_toggle_li in year_toggle_lis:
                    year = year_toggle_li.text.strip()
                    year_link = 'https://www.cadillac.com' + year_toggle_li.a['href']
                    year_link_soup = BeautifulSoup(requests.get(url=year_link).content, 'html5lib')
                    if year_link_soup.find_all('div', {'class': 'q-content content active-override'}) and 'preceding-year' not in year_link:
                        overrides = year_link_soup.find_all('div', {'class': 'q-content content active-override'})
                        print(year_link, '---------------------------------------------------')
                        for override in overrides:
                            section = override.find('span', {'class': 'q-headline-text q-button-text'}).text.strip()
                            titles_desc = override.select('.row.q-gridbuilder.grid-bg-color-one')
                            print(section)
                            for title_desc in titles_desc:
                                ttitle_desc = title_desc.find_all('div', recursive=False)
                                for t_desc in ttitle_desc:
                                    if not t_desc.picture:
                                        continue
                                    image = 'https://www.cadillac.com' + t_desc.picture.img['src']
                                    if len(t_desc.select('.q-margin-base .q-text.q-body1')) < 2:
                                        continue
                                    title = t_desc.select('.q-margin-base .q-text.q-body1')[0].text.strip()
                                    description = t_desc.select('.q-margin-base .q-text.q-body1')[1].text.strip()
                                    if len(title) < 3:
                                        continue
                                    line = [year, 'Cadillac', model, section, title, description, image]
                                    if line not in lines:
                                        lines.append(line)
                                        print(line)
                                        self.chevrolet.write_csv(lines=[line], filename='Cadillac_2019_2020.csv')
                    else:
                        previous_year = year_toggle_lis[1].text.strip()
                        previous_link = 'https://www.cadillac.com' + year_toggle_lis[1].a['href']
                        year_link_soup = BeautifulSoup(requests.get(url=previous_link).content, 'html5lib')
                        feature_link = 'https://www.cadillac.com' + year_link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']
                        print(feature_link, '==========================')
                        feature_link_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
                        separators = feature_link_soup.select('.q-content.content.active-override')
                        for separator in separators:
                            if separator.find(class_='q-headline1').style:
                                separator.find(class_='q-headline1').style.decompose()
                            title = separator.find(class_='q-headline1').text.strip()
                            description = separator.find(class_='q-text q-body1').text.strip()
                            image = 'https://www.cadillac.com' + separator.find('picture').img['src']
                            section = find_parent_under_body(separator).find_previous('div', {'class': 'q-margin-base q-headline'}).text.strip()
                            if len(title) < 3:
                                continue
                            line = [previous_year, 'Cadillac', model, section, title, description, image]
                            if line not in lines:
                                lines.append(line)
                                print(line)
                                self.chevrolet.write_csv(lines=[line], filename='Cadillac_2019_2020.csv')
                        reference_partial = feature_link_soup.find('div', {'class': 'q-margin-base q-reference-partial'})
                        if reference_partial:
                            titles_dom = reference_partial.find_all('div', {'class': 'q-margin-base q-headline'})
                            for title_dom in titles_dom:
                                if not title_dom.find('h1', {'class': 'q-headline2'}):
                                    continue
                                title = title_dom.find('h1', {'class': 'q-headline2'}).text.strip()
                                description = title_dom.find_next('p').text.strip()
                                image = 'https://www.cadillac.com' + title_dom.find_previous('picture').img['src']
                                if len(title) < 3:
                                    continue
                                line = [previous_year, 'Cadillac', model, 'Technology', title, description, image]
                                if line not in lines:
                                    lines.append(line)
                                    print(line)
                                    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                                    self.chevrolet.write_csv(lines=[line], filename='Cadillac_2019_2020.csv')
            else:
                overrides = link_soup.find_all('div', {'class': 'q-content content active-override'})
                print(link, '---------------------------------------------------')
                for override in overrides:
                    section = override.find('span', {'class': 'q-headline-text q-button-text'}).text.strip()
                    titles_desc = override.select('.row.q-gridbuilder.grid-bg-color-one')
                    for title_desc in titles_desc:
                        ttitle_desc = title_desc.find_all('div', recursive=False)
                        for t_desc in ttitle_desc:
                            if not t_desc.picture:
                                continue
                            image = 'https://www.cadillac.com' + t_desc.picture.img['src']
                            if len(t_desc.select('.q-margin-base .q-text.q-body1')) < 2:
                                continue
                            title = t_desc.select('.q-margin-base .q-text.q-body1')[0].text.strip()
                            description = t_desc.select('.q-margin-base .q-text.q-body1')[1].text.strip()
                            if len(title) < 3:
                                continue
                            line = ['2020', 'Cadillac', model, section, title, description, image]
                            if line not in lines:
                                lines.append(line)
                                print(line)
                                self.chevrolet.write_csv(lines=[line], filename='Cadillac_2019_2020.csv')
                year = model[:4]
                model = model[4:].strip()
                if 'https://www.cadillac.com' in link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']:
                    feature_link = link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']
                else:
                    feature_link = 'https://www.cadillac.com' + link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']
                print(feature_link, '+++++++++++++++++++++++++++++++++++++++')
                year_link_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
                if not year_link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a'):
                    continue
                feature_link = 'https://www.cadillac.com' + \
                               year_link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']
                feature_link_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
                separators = feature_link_soup.select('.q-content.content.active-override')
                for separator in separators:
                    title = separator.find_all(class_='q-headline1')[-1].text.strip()
                    description = separator.find(class_='q-text q-body1').text.strip()
                    image = 'https://www.cadillac.com' + separator.find('picture').img['src']
                    section = find_parent_under_body(separator).find_previous('div', {
                        'class': 'q-margin-base q-headline'}).text.strip()
                    line = [year, 'Cadillac', model, section, title, description, image]
                    if line not in lines:
                        lines.append(line)
                        print(line)
                        self.chevrolet.write_csv(lines=[line], filename='Cadillac_2019_2020.csv')

    def Fiat(self):
        links = ['https://www.fiat.com//fiat-500', 'https://www.fiat.com//fiat-500c', 'https://www.fiat.com//fiat-500x', 'https://www.fiat.com//fiat-500l', 'https://www.fiat.com//panda', 'https://www.fiat.com//tipo', 'https://www.fiat.com//124-spider', 'https://www.fiat.com//qubo', 'https://www.fiat.com//doblo', 'https://www.fiat.com//fiat-concept-centoventi']
        for link in links:
            link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')


    def GMC(self):
        lines = []
        initial_url = 'https://www.gmc.com/navigation/navigation-flyouts/vehicles.html'
        initial_soup = BeautifulSoup(requests.get(url=initial_url).content, 'html5lib')
        vehicles = initial_soup.select('a[class=stat-image-link]')
        for vehicle in vehicles:
            vehicle_url = 'https://www.gmc.com' + vehicle['href']
            vehicle_soup = BeautifulSoup(requests.get(url=vehicle_url).content, 'html5lib')
            if not vehicle_soup.find('div', {'class': 'q-sibling-nav-container'}):
                continue
            sibling_nav = vehicle_soup.find('div', {'class': 'q-sibling-nav-container'})
            feature_nav = sibling_nav.find('span', text='FEATURES')
            if feature_nav:
                feature_link = 'https://www.gmc.com' + feature_nav.find_parent('a')['href']
                feature_link_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
                years_nav = feature_link_soup.select('.q-nav-container .q-year-toggle-list a')
                for year_nav in years_nav:
                    year = year_nav.text.strip()
                    year_link = 'https://www.gmc.com' + year_nav['href']
                    year_link_soup = BeautifulSoup(requests.get(url=year_link).content, 'html5lib')
                    model = year_link_soup.select('.q-nav-container > a > span')[0].text[4:].strip()
                    sections_dom = year_link_soup.find_all('li', {'class': 'q-js-tirtiary-item'})
                    for section_dom in sections_dom:
                        section = section_dom.text.strip()
                        section_link = 'https://www.gmc.com' + section_dom.a['href']
                        section_link_soup = BeautifulSoup(requests.get(url=section_link).content, 'html5lib')
                        titles_dom = section_link_soup.select('.q-margin-base .q-text.q-body1')
                        for title_dom in titles_dom:
                            if 'gmc.com' not in title_dom.find_previous('a')['href']:
                                description_link = 'https://www.gmc.com' + title_dom.find_previous('a')['href']
                            else:
                                description_link = title_dom.find_previous('a')['href']
                            if not BeautifulSoup(requests.get(url=description_link).content, 'html.parser').select('.q-text.q-body1'):
                                continue
                            description = BeautifulSoup(requests.get(url=description_link).content, 'html.parser').select('.q-text.q-body1')[0].text.strip()
                            title = title_dom.text.strip()
                            if not title_dom.find_previous('img').has_attr('src'):
                                continue
                            image = 'https://www.gmc.com' + title_dom.find_previous('img')['src']
                            line = [year, 'GMC', model, section, title, description, image]
                            if line not in lines:
                                lines.append(line)
                                print(line)
                                self.chevrolet.write_csv(lines=[line], filename='GMC_2019_2020.csv')
            else:
                rights_nav = vehicle_soup.select('ul.q-scroller-list.q-sibling-nav-list.inline-list > li.hide-for-large-down a')
                for right_nav in rights_nav:
                    right_nav_link = 'https://www.gmc.com' + right_nav['href']
                    right_nav_link_soup = BeautifulSoup(requests.get(url=right_nav_link).content, 'html5lib')
                    if not right_nav_link_soup.find('div', {'class': 'q-sibling-nav-container'}):
                        continue
                    sibling_nav = right_nav_link_soup.find('div', {'class': 'q-sibling-nav-container'})
                    feature_nav = sibling_nav.find('span', text='FEATURES')
                    if feature_nav:
                        feature_link = 'https://www.gmc.com' + feature_nav.find_parent('a')['href']
                        feature_link_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
                        years_nav = feature_link_soup.select('.q-nav-container .q-year-toggle-list a')
                        for year_nav in years_nav:
                            year = year_nav.text.strip()
                            year_link = 'https://www.gmc.com' + year_nav['href']
                            year_link_soup = BeautifulSoup(requests.get(url=year_link).content, 'html5lib')
                            model = year_link_soup.select('.q-nav-container > a > span')[0].text[4:].strip()
                            sections_dom = year_link_soup.find_all('li', {'class': 'q-js-tirtiary-item'})
                            for section_dom in sections_dom:
                                section = section_dom.text.strip()
                                section_link = 'https://www.gmc.com' + section_dom.a['href']
                                section_link_soup = BeautifulSoup(requests.get(url=section_link).content, 'html5lib')
                                titles_dom = section_link_soup.select('.q-margin-base .q-text.q-body1')
                                for title_dom in titles_dom:
                                    if 'gmc.com' not in title_dom.find_previous('a')['href']:
                                        description_link = 'https://www.gmc.com' + title_dom.find_previous('a')['href']
                                    else:
                                        description_link = title_dom.find_previous('a')['href']
                                    if not BeautifulSoup(requests.get(url=description_link).content,
                                                         'html.parser').select('.q-text.q-body1'):
                                        continue
                                    description = \
                                    BeautifulSoup(requests.get(url=description_link).content, 'html.parser').select(
                                        '.q-text.q-body1')[0].text.strip()
                                    title = title_dom.text.strip()
                                    if not title_dom.find_previous('img').has_attr('src'):
                                        continue
                                    image = 'https://www.gmc.com' + title_dom.find_previous('img')['src']
                                    line = [year, 'GMC', model, section, title, description, image]
                                    if line not in lines:
                                        lines.append(line)
                                        print(line)
                                        self.chevrolet.write_csv(lines=[line], filename='GMC_2019_2020.csv')


print("=======================Start=============================")
if __name__ == '__main__':
    features_2020 = Features_2020()
    features_2020.GMC()
    ford = Ford()
    acura = Acura()
    audi = Audi()
    buick = Buick()
    toyota = Toyota()
    chevrolet = Chevrolet()
    chevrolet_count = Chevrolet_count()
    sheet_arrange = Sheet_arrange()
    # sheet_arrange.sort()
print("=======================The End===========================")
