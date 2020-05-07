import xlrd
from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import csv
from random import choice


FILENAME = 'парс.xlsx'

page_data = []

# reading useragents and proxies from files
proxies = open('ips').read().split('\n')
useragents = open('useragents').read().split('\n')

# reading data from excel file
def read_file(filename):
    data = []
    rb = xlrd.open_workbook(filename)
    sheet = rb.sheet_by_index(1)
    for rownum in range(sheet.nrows):
        row = sheet.row_values(rownum)
        try:
            element = (int(row[1]), row[3])
            data.append(element)
        except ValueError:
            continue
    return data

# get url list
def get_urls(queries):
    urls = []
    
    for query in queries:
        base_url = 'https://th-tool.by/index.php?route=product/product&'
        product_id = f'product_id={query[0]}'
        search = f'search={query[1]}'

        search_url = f'{base_url}{product_id}{search}'

        urls.append(search_url)
    return (urls)

# get response from server with other useragents and ip
def get_html(URL):
    proxy = {'http': 'http://' + choice(proxies)}
    useragent = {'User-Agent': choice(useragents)}

    response = requests.get(URL, headers=useragent, proxies=proxy)
    print('geted')
    return response.text

# Find image on html page, and return tuple
def get_images(html):

    soup = BeautifulSoup(html, 'html.parser')
    main_image = soup.find(id="imageWrap").find('a').get('href')
    try:
        secondary_images = soup.find(id="owl-images").find_all('a')
        secondary_images = [img.get('href') for img in secondary_images if img]
        print(secondary_images)
        s = ''
        for im in secondary_images:
            s = s+im+';'
    except AttributeError:
        s = 'None'

    page_image_data = (main_image, s)
    return page_image_data


# Write parsed data to csv
def collect_data(images):
    with open('r.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(
            (images[0],
            images[1],)
        )
        
# Method doing all taks
def make_all(url):
    html = get_html(url)
    images = get_images(html)
    collect_data(images)

# Run task wit multiprocessing
url_list = get_urls(read_file(FILENAME))

with Pool(10) as pool:
    pool.map(make_all, url_list)


