import requests
from bs4 import BeautifulSoup
import urllib.request


initial_url = 'https://www.globalcarsbrands.com/all-car-brands-list-and-logos/'
cols = BeautifulSoup(requests.get(url=initial_url).text, 'html.parser').select('#brandlogos .logo_col')
print(len(cols))
for col in cols:
    try:
        image_url = col.select('div.brand_img_box>a>img')[0]['src']
    except:
        image_url = col.select('div.brand_img_box>img')[0]['src']
    try:
        name = col.select('div.brand_name>a')[0].text
    except:
        name = col.select('div.brand_name')[0].text
    file_name = image_url.split('/')[-1]
    urllib.request.urlretrieve(image_url, 'logos/' + file_name)

    print(image_url, name)