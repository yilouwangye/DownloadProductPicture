# !usr/bin/env python
# -*-coding:utf-8 -*-

# @FileName: DownloadProductPocture.py
# @Author:tian

import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import os
import time
from downlodpicture.config import *

class productPictrue():
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=self.option)
        self.wait = WebDriverWait(self.driver,30)
        self.client = MongoClient(MONGO_CLIENT)

    def bowser_init(self,html):
        '''
        :param html:product url
        :return:
        '''
        self.driver.get(html)

    def get_main_img(self,html):
        '''
        :param html:
        :return:
        '''
        try:
            self.driver.get(html)
            time.sleep(5)
            main_img_url = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.van-swipe-item img')))
            for i, item in enumerate(main_img_url):
                if i % 2 == 0:
                    yield {
                        'index':int(i / 2 + 1),
                        'url':item.get_attribute('src')
                    }
        except(NoSuchElementException,TimeoutException) as e:
            print(e)

    def get_descrip_img(self,html):
       '''
       :param html:
       :return:
       '''
       try:
            time.sleep(5)
            des_img_url = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'#pics img')))
            for i, item in enumerate(des_img_url):
                yield {
                    'index':i + 1,
                    'url':item.get_attribute('src')
                }
       except(NoSuchElementException,TimeoutException):
          print('No element or timeout!')

    def save_file(self,url,path):
        '''
        :param url:image url
        :param path: save path
        :return:
        '''
        response = requests.get(url)
        if response.status_code == 200:
            with open(path,'wb') as f:
                f.write(response.content)
                f.close()

    def get_sku_id(self,prod):
        '''
        :param prod: target products
        :return:
        '''
        db = self.client[MONGO_DB]
        col = db[MONGO_COL]
        condition = prod.strip('\n').split('\n')
        results = col.find({'sku_num': {'$in': condition}})
        for result in results:
            yield {
                'sku_id':result['sku_id'],
                'sku_num':result['sku_num'],
                'prod_id':result['prod_id']
            }

    def main(self):
        '''
        :return:
        '''
        base_url = BASE_URL
        for sku in self.get_sku_id(prod):
            html = base_url + str(sku['prod_id']) + '&skid=' + str(sku['sku_id'])
            self.bowser_init(html)
            path = PATH
            try:
                if not os.path.exists(sku['sku_num']):
                    os.makedirs(path+'/'+sku['sku_num']+'/1000X1000')
                    os.makedirs(path+'/'+sku['sku_num']+'/description')
            except Exception as e:
                print(e)
                print('文件已存在')
            for item in self.get_main_img(html):
                self.save_file(item['url'],path+'/'+sku['sku_num']+'/1000X1000/'+str(item['index'])+'.jpg')
            print(f'{sku["sku_num"]}主图已下载..')
            for item in self.get_descrip_img(html):
                self.save_file(item['url'],path+'/'+sku['sku_num']+'/description/'+str(item['index'])+'.jpg')
            print(f'{sku["sku_num"]}详情图已下载..')
            time.sleep(5)
        self.driver.quit()

if __name__ == '__main__':
    prod = '''
A0003006302
A0005029200D
'''
    d = productPictrue()
    d.main()