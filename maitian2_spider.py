import requests
from requests import RequestException
from lxml import etree
import pymongo

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
}
result = []
proxy = None
max_count = 5
mong_py = pymongo.MongoClient()
collection = mong_py.mymo.maitian

def get_proxy():
    proxy_url = 'http://127.0.0.1:5555/random'
    try:
        response = requests.get(proxy_url,headers = headers)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url,count = 1):
    global proxy
    if count >= max_count:
        print('请求次数过多')
        return None

    try:
        if proxy:
            proxies = {
                'http' : 'http://' + proxy
            }
            response = requests.get(url, headers = headers, allow_redirects = False, proxies = proxies)
        else:
            response = requests.get(url, headers=headers, allow_redirects=False)
        if response.status_code == 200:
            return response.text
        if response.status_code == 403:
            print('403')
            proxy = get_proxy()
            if proxy:
                print('User proxy',proxy)
                return get_html(url)
            else:
                print('get proxy none')
                return None
    except ConnectionError as e:
        print('Error Occurred' , e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url,count)

def parse_html(html):
    data = etree.HTML(html)
    start = data.xpath('//li/div[@class="list_title"]')
    for item in start:
        a = {}
        a['title'] = item.xpath('./h1/a/text()')[0].replace('\r\n','').strip()
        a['price'] = item.xpath('./div[@class="the_price"]/ol/strong/span/text()')[0] + '/月'
        a['area'] = item.xpath('./p[1]/span[1]/text()')[0]
        a['address'] = item.xpath('./p[@class="house_hot"]/span/text()')[0].replace('\r\n','').strip()
        a['d_address'] = item.xpath('./p[@class="house_hot"]/span/text()')[1].replace('\r\n','').replace('\xa0',' ').strip()
        result.append(a)

def main(pg):
    url = 'http://bj.maitian.cn/zfall/PG' + str(pg)
    print(url)
    html = get_html(url)
    parse_html(html)

if __name__ == '__main__':
    for i in range(1,101):
        main(i)
    for i in result:
        print(i)
    collection.insert_many(result)