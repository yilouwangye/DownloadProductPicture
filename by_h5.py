# !usr/bin/env python
# -*-coding:utf-8 -*-

# @FileName: DownloadProductPocture.py
# @Author:tian
# @Time:05/16/2020

import requests
from selenium import webdriver
from requests.exceptions import RequestException
import os
import time
import pymongo

def get_main_img(html):
    '''解析获取商品主图'''
    try:
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        browser = webdriver.Chrome(chrome_options=option)
        browser.get(html)
        time.sleep(5)
        main_img_url = browser.find_elements_by_css_selector('.van-swipe-item img')
        for i, item in enumerate(main_img_url):
            if i % 2 == 0:
                yield {
                    'index':int(i / 2 + 1),
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
    time.sleep(5)
    des_img_url = browser.find_elements_by_css_selector('#pics img')
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
    print(condition)
    results = col.find({'sku_num': {'$in': condition}})
    for result in results:
        yield {
            'sku_id':result['sku_id'],
            'sku_num':result['sku_num'],
            'prod_id':result['prod_id']
        }



def main():
    '''主函数main'''
    base_url = 'https://mall.gree.com/mobile-h5/index.html#/detail?id='

    for sku in get_sku_id(prod):
        html = base_url + str(sku['prod_id']) + '&skid=' + str(sku['sku_id'])
        file = r'C:\Users\Administrator\Desktop\00'
        try:
            if not os.path.exists(sku['sku_num']):
                os.makedirs(file+'/'+sku['sku_num']+'/1000X1000')
                os.makedirs(file+'/'+sku['sku_num']+'/description')
        except Exception:
            print('文件已存在')
        for item in get_main_img(html):
            '''下载主图'''
            save_file(item['url'],file+'/'+sku['sku_num']+'/1000X1000/'+str(item['index'])+'.jpg')
        print(f'{sku["sku_num"]}主图已下载..')
        for item in get_descrip_img(html):
            '''下载详情图'''
            save_file(item['url'],file+'/'+sku['sku_num']+'/description/'+str(item['index'])+'.jpg')
        print(f'{sku["sku_num"]}详情图已下载..')
        time.sleep(5)
if __name__ == '__main__':
    prod = '''
MP026010300
MP026009700
KB468000800
9511694001_
102010112_
'''
    main()
