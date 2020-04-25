# !usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from selenium import webdriver
from requests.exceptions import RequestException
import os
import time
import pymongo


def get_page(url):
    '''获取页面信息'''
    try:
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type':'text/html;charset=UTF-8'
        }
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.content
        return None
    except RequestException:
        return None

def get_main_img(html):
    '''解析获取商品主图'''
    try:
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        browser = webdriver.Chrome(chrome_options=option)
        browser.get(html)
        main_img_url = browser.find_elements_by_css_selector('#imageMenu li img')
        for i, item in enumerate(main_img_url):
            yield {
                'index':i + 1,
                'url':item.get_attribute('src')
            }
    finally:
        browser.close()

def get_descrip_img(html):
    '''解析获取商品详情图'''
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=option)
    browser.get(html)
    des_img_url = browser.find_elements_by_css_selector('#right_pic_2 img')
    for i, item in enumerate(des_img_url):
        yield {
            'index':i + 1,
            'url':item.get_attribute('src')
        }

def save_file(url,path):
    '''下载img，保存'''
    response = requests.get(url)
    if response.status_code == 200:
        with open(path,'wb') as f:
            f.write(response.content)
            f.close()

def get_sku_id(prod):
    '''对应sku_id'''
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.country
    col = db.shop
    condition = prod.strip('\n').split('\n')
    results = col.find({'sku_num': {'$in': condition}})
    for result in results:
        yield {
            'sku_id_url':result['sku_id'],
            'sku_num':result['sku_num']
        }

prod = '''
B6001008400D
B4001003600
B3001901900
A0013000800
A0011009700

'''

def main():
    '''主函数main'''
    base_url = 'https://mall.gree.com/goods/product/details?id='

    for sku in get_sku_id(prod):
        html = base_url + str(sku['sku_id_url'])
        file = r'file path\product'
        try:
            if not os.path.exists(sku['sku_num']):
                os.makedirs(file+'/'+sku['sku_num']+'/1000X1000')
                os.makedirs(file+'/'+sku['sku_num']+'/description')
        except Exception:
            print('文件已存在')
        for item in get_main_img(html):
            '''下载主图'''
            print(item)
            save_file(item['url'],file+'/'+sku['sku_num']+'/1000X1000/'+str(item['index'])+'.jpg')
        for item in get_descrip_img(html):
            '''下载详情图'''
            print(item)
            save_file(item['url'],file+'/'+sku['sku_num']+'/description/'+str(item['index'])+'.jpg')
        time.sleep(5)
if __name__ == '__main__':
    main()
