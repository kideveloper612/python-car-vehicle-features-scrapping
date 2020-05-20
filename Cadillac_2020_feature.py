import requests
from bs4 import BeautifulSoup
import os
import csv
csv_header = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'IMAGE']]


def find_parent_under_body(ele):
    if ele.parent.name == 'body':
        return ele
    return ele.parent


def write_direct_csv(lines, filename):
    with open(filename, 'a', encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)
    csv_file.close()


def write_csv(lines, filename):
    if not os.path.isfile(filename):
        write_direct_csv(lines=csv_header, filename=filename)
    write_direct_csv(lines=lines, filename=filename)


lines = []
links = ['https://www.cadillac.com/sedans/ct4', 'https://www.cadillac.com/sedans/ct4#ct4-v',
         'https://www.cadillac.com/sedans/ct5', 'https://www.cadillac.com/sedans/ct5#ct5-v',
         'https://www.cadillac.com/sedans/cts-sedan', 'https://www.cadillac.com/sedans/ct6',
         'https://www.cadillac.com/sedans/ct6-v'
         ]
for link in links:
    link_soup = BeautifulSoup(requests.get(url=link).content, 'html5lib')
    model = link_soup.select('#nav_anchor > span')[0].text.strip()
    year_toggle_lis = link_soup.select('.q-year-toggle-list li')
    if len(year_toggle_lis) != 2:
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
                        write_csv(lines=[line], filename='Cadillac_Sedans_2020.csv')
        year = model[:4]
        model = model[4:].strip()
        if 'https://www.cadillac.com' in link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']:
            feature_link = link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']
        else:
            feature_link = 'https://www.cadillac.com' + \
                           link_soup.select('.q-sibling-nav-container ul > li:nth-child(2) a')[0]['href']
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
                write_csv(lines=[line], filename='Cadillac_Sedans_2020.csv')