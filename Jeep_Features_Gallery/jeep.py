import requests
import os
import csv
from bs4 import BeautifulSoup
import re
import json

csv_header = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'TITLE', 'DESCRIPTION', 'IMAGE']]
def write_direct_csv(lines, filename):
    with open('output/%s' % filename, 'a', encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)
    csv_file.close()


def write_csv(lines, filename):
    if not os.path.isdir('output'):
        os.mkdir('output')
    if not os.path.isfile('output/%s' % filename):
        write_direct_csv(lines=csv_header, filename=filename)
    write_direct_csv(lines=lines, filename=filename)


def Jeep():
    lines = []
    initial_url = 'https://www.jeep.com/all-vehicles.html'
    initial_soup = BeautifulSoup(requests.request('GET', url=initial_url).content, 'html5lib')
    vehicles = initial_soup.select(
        '#flyout-vehicles > div > div.nav-flyout-container > div > div > div > div > div > a')
    for vehicle in vehicles:
        vehicle_link = 'https://jeep.com' + vehicle['href']
        vehicle_name = vehicle.find('span', attrs={'data-cats-id': 'vehicle-name'}).text.strip()
        vehicle_soup = BeautifulSoup(requests.request('GET', url=vehicle_link).content, 'html5lib')
        features = vehicle_soup.select('ul.secondary-section-link-list.gcss-theme-light:nth-child(1) a')
        for feature in features:
            category = feature.text.strip()
            if '#' in feature['href']:
                break
            if 'gallery' in feature['href']:
                continue
            if 'OVERVIEW' == category.upper():
                continue
            feature_link = 'https://jeep.com' + feature['href']
            feature_soup = BeautifulSoup(requests.get(url=feature_link).content, 'html5lib')
            titles = feature_soup.find_all(re.compile('h'), class_=re.compile('title'))
            print(feature_link)
            for t in titles:
                title = t.text.strip()
                if t.find_next(class_=re.compile('description')):
                    if 'READY, WILLING AND ABLE' in title:
                        ready_json = json.loads(t.find_previous(attrs={'data-props': True})['data-props'])
                        title = ready_json['contentBox']['title'].strip()
                        description = ready_json['contentBox']['contentModules'][0]['content']['paragraphCopy'].replace('<p>', '').replace('</p>', '').strip()
                        image_url = 'https://jeep.com' + ready_json['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
                    if t.find(attrs={'title gcss-typography-brand-heading-4': True}):
                        gcs_prop = json.loads(t.find_previous(attrs={'data-props': True})['data-props'])
                        title = gcs_prop['contentBox']['title'].strip()
                        description = gcs_prop['contentBox']['contentModules'][0]['content']['paragraphCopy'].strip()
                        image_url = gcs_prop['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
                    description = t.find_next(class_=re.compile('description')).text.strip()
                    prop = t.find_next(attrs={'data-props': True})
                    prop_json = json.loads(prop['data-props'])
                    if 'media' in prop_json:
                        image_url = 'https://jeep.com' + prop_json['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
                    elif 'tabsContent' in prop_json:
                        selectorsContent = prop_json['tabsContent'][0]['selectorsContent']
                        for selectorContent in selectorsContent:
                            if 'assets' in selectorContent['content']:
                                image_url = 'https://jeep.com' + selectorContent['content']['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                                title = selectorContent['content']['contentBox']['title'].strip()
                                if selectorContent['content']['contentBox']['contentModules']:
                                    description = selectorContent['content']['contentBox']['contentModules'][0]['content']['paragraphCopy'].replace('<p>', '').replace('</p>', '').strip()
                                    line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                                    if line not in lines:
                                        print(line)
                                        lines.append(line)
                        selectors = prop_json['tabsContent'][0]['selectorGroup']['selectors']
                        for selector in selectors:
                            tmp_title = selector['title'].strip()
                            tmp_description = selector['description'].strip()
                            if 'image' in selector:
                                tmp_image_link = 'https://jeep.com' + selector['image']['lg'][0]
                                line = ['2020', 'Jeep', vehicle_name, category, tmp_title, tmp_description, tmp_image_link]
                                if line not in lines:
                                    print(line)
                                    lines.append(line)
                    elif 'displayMediaLeft' in prop_json:
                        image_url = 'https://jeep.com' + prop_json['displayMediaLeft']['media']['mediaAsset']['image']['lg'][0]
                        add_image = 'https://jeep.com' + prop_json['displayMediaRight']['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url, add_image]
                        if line not in lines:
                            print(line)
                            lines.append(line)
                    elif 'views' in prop_json and 'hasHorizontalPadding' in prop_json:
                        image_url = 'https://jeep.com' + prop_json['views'][0]['categorySwatches'][0]['swatchList'][0]['swatches'][0]['data']['asset'][0]['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
                    elif 'assets' in prop_json:
                        image_url = 'https://jeep.com' + prop_json['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
                    elif 'featuresContent' in prop_json:
                        featuresContent = prop_json['featuresContent']
                        for featureContent in featuresContent:
                            image_url = 'https://jeep.com' + featureContent['content']['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                            title = featureContent['content']['contentBox']['title'].strip()
                            description = featureContent['content']['contentBox']['contentModules'][0]['content']['paragraphCopy'].replace('<p>', '').replace('</p>', '').strip()
                            line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                            if line not in lines:
                                print(line)
                                lines.append(line)
                    elif 'carouselData' in prop_json:
                        panels = prop_json['carouselData']['panels']
                        for panel in panels:
                            image_url = 'https://jeep.com' + panel['openheropanel']['desktopMedia']['asset']['media']['mediaAsset']['image']['lg'][0]
                            line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                            if line not in lines:
                                print(line)
                                lines.append(line)
                    elif 'row2' in prop_json and 'mediaAsset' in prop_json['row2']['props']['displayMedia']:
                        image_url = 'https://jeep.com' + prop_json['row2']['props']['displayMedia']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
            additions = feature_soup.find_all('p', {'class': 'text-size-3'})
            for addition in additions:
                title = addition.text.strip()
                if addition.find_next('p', {'class': 'text-align--center'}):
                    description = addition.find_next('p', {'class': 'text-align--center'}).text.strip()
                    addition_prop = json.loads(addition.find_previous(attrs={'data-props': True})['data-props'])
                    image_url = addition_prop['carouselData']['panels'][0]['openheropanel']['desktopMedia']['asset']['media']['mediaAsset']['image']['lg'][0]
                    line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                    if line not in lines:
                        print(line)
                        lines.append(line)
            again_props = feature_soup.find_all(attrs={'data-props': True})
            for again_prop in again_props:
                again_json = json.loads(again_prop['data-props'])
                if 'blurbList' in again_json:
                    blurbs = again_json['blurbList']
                    for blurb in blurbs:
                        if 'label' in blurb:
                            title = blurb['label']['labelText'].strip()
                            description = blurb['description']['descText'].strip()
                            image_url = 'https://jeep.com' + blurb['displayMedia']['media']['mediaAsset']['image']['lg'][0]
                            line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                            if line not in lines:
                                print(line)
                                lines.append(line)
                elif 'row2' in again_json and again_json['row2'] and isinstance(again_json['row2'], list) and 'props' in again_json['row2'][0]:
                    print(again_json['row2'])
                    title = again_json['row2'][0]['props']['descriptionBlock']['title'].strip()
                    description = again_json['row2']['props']['descriptionBlock']['contentModules'][0]['content']['paragraphCopy']
                    image_url = 'https://jeep.com' + again_json['row2']['props']['displayMedia']['media']['mediaAsset']['image']['lg'][0]
                    line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                    if line not in lines:
                        print(line)
                        lines.append(line)
                elif 'contentBox' in again_json and 'contentModules' in again_json['contentBox'] and again_json['contentBox']['contentModules']:
                    title = again_json['contentBox']['title'].strip()
                    description = again_json['contentBox']['contentModules'][0]['content']['paragraphCopy']
                    image_url = 'https://jeep.com' + again_json['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                    line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                    if line not in lines:
                        print(line)
                        lines.append(line)
                elif 'featuresContent' in again_json:
                    featuresContent = again_json['featuresContent']
                    for featureContent in featuresContent:
                        title = featureContent['content']['contentBox']['title'].strip()
                        description = featureContent['content']['contentBox']['contentModules'][0]['content']['paragraphCopy'].replace('<p>', '').replace('</p>', '').strip()
                        image_url = 'https://jeep.com' + featureContent['content']['assets'][0]['content']['media']['mediaAsset']['image']['lg'][0]
                        line = ['2020', 'Jeep', vehicle_name, category, title, description, image_url]
                        if line not in lines:
                            print(line)
                            lines.append(line)
    print('=================================================From Save===============================================')
    write_csv(lines=lines, filename='Jeep_Feature.csv')


def arrange():
    images = []
    file_path = 'output/Jeep_Feature_3.csv'
    with open(file=file_path, encoding='utf-8') as csv_reader:
        readers = csv.reader(csv_reader, delimiter=',')
        for reader in readers:
            if reader[6] in images:
                continue
            images.append(reader[6])
            write_csv(lines=[reader], filename='fdsf.csv')
            print(reader)


if __name__ == '__main__':
    print('================================= Start ====================================')
    Jeep()
    arrange()
    print('================================== End ====================================')
