#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 20:04:38 2018

@author: clytie
"""
import os
import pandas as pd
from collections import defaultdict
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys

def get_basic(driver):
    basic_combo = {}
    basic_combo['title_text'] = driver.find_element_by_css_selector("div.sku-name").text
    
    elem = driver.find_element_by_css_selector("span.p-price")
    basic_combo['price'] = elem.text
	
    detail = driver.find_element_by_css_selector(".p-parameter")
    basic_combo['detail'] = detail.text
    return basic_combo
                                  

def get_all_comment(driver):
    comment = []
    path = "div.comment-item:nth-child(%s)"
    last_page = 0
    page_cur = 1
    page = 0
    while 1: #改成1
        item = 1
        while last_page != page_cur:
            try:
                comment_item = driver.find_element_by_css_selector(path % str(item))
                for i in xrange(1, 6):
                    try:
                        driver.find_element_by_css_selector(path % str(item) + " .star" + str(i))
                        star = i
                        break
                    except:
                        pass
                comment_dict = {}
                comment_dict[star] = comment_item.text
                comment.append(comment_dict)
                item += 1
            except:
                break
        
        last_page = int(driver.find_element_by_css_selector("a.ui-page-curr").text)
        
        if len(comment) < 10 * page:
            break
        
        if driver.find_element_by_css_selector("a.ui-pager-next").text == u"下一页":
            while 1:
                try:
                    driver.find_element_by_css_selector("a.ui-pager-next").click()
                    time.sleep(3)
                    page_cur = int(driver.find_element_by_css_selector("a.ui-page-curr").text)
                    break
                except:
                    for _ in xrange(5):
                        driver.find_element_by_css_selector("body").send_keys(Keys.DOWN)
        else:
            break
        page += 1
        if not page_cur % 10:
            print "page %s finished" % page_cur
    return page, comment

def save_info(basic, comment, table_name):
    df1 = pd.DataFrame(index=[0])
    df1["detail"] = basic["detail"]
    df1["price"] = basic["price"]
    df1["title_text"] = basic["title_text"]
    df1.to_csv(table_name + "detail.csv", encoding = "utf-8")
    df2 = pd.DataFrame()
    index = 0
    for comment_item in comment:
        df2 = df2.append(pd.DataFrame(comment_item.items(), columns = ["star", "comment"], index = [index]))
        index += 1
    df2.to_csv(table_name + "comment.csv", encoding = "utf-8")
    

def get_phone(driver):
    lost_item = defaultdict(list)
    driver.switch_to_window(driver.window_handles[0])
    path = "li.gl-item:nth-child(%s) > div:nth-child(1) > div:nth-child(4) > a:nth-child(1) > em:nth-child(1)"
    
    last_page = 0
    curr_page = 1
    PAGE = 0
    while PAGE < 100: #改成100
        item = 1

        dir_name = "PHONE" + str(curr_page)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        while last_page != curr_page:
            while item <= 60:
                for count in xrange(3):
                    try:
                        driver.switch_to_window(driver.window_handles[0])
                        driver.find_element_by_css_selector(path % str(item)).click()
                        if len(driver.window_handles) > 2:
                            driver.switch_to_window(driver.window_handles[2])
                            driver.close()
                        time.sleep(5)
                        driver.switch_to_window(driver.window_handles[1])
                        
                        basic = get_basic(driver)     
                        
                        driver.find_element_by_css_selector("#detail > div:nth-child(1) > ul:nth-child(1) > li:nth-child(5)").click()
                        page, comment = get_all_comment(driver)
                        
                        if len(comment) <= 20:
                            print "未刷新出下一页,重新刷新"
                            driver.close()
                            driver.switch_to_window(driver.window_handles[0])
                            raise Exception("comment number error.")
                        
                        save_info(basic, comment, os.path.join(dir_name, str(item)))
                        print "item %s finished" % item
                        print "=" * 50
                        
                        driver.close()
                        driver.switch_to_window(driver.window_handles[0])
                        
                        item += 1
                        flag = 0
                        break
                    except:
                        for _ in xrange(3):    
                            driver.find_element_by_css_selector("body").send_keys(Keys.DOWN)
                        flag = 1
                if flag:
                    print "item %s lost" % item
                    print "=" * 50
                    lost_item[curr_page].append(item)
                    item += 1
                    
            if item > 60: #改成60
                break #退出last_page!=curr_page循环
        driver.switch_to_window(driver.window_handles[0])
        last_page = int(driver.find_element_by_css_selector(".fp-text > b:nth-child(1)").text)
        print "+" * 50
        print "page %s finished" % last_page
        print "+" * 50
        
        for _ in xrange(3):
            try:
                driver.find_element_by_css_selector("body").send_keys(Keys.RIGHT)
                time.sleep(2)
                break
            except:
                print "page %s 未跳到下一页,重新跳到下一页 " % curr_page
        curr_page = int(driver.find_element_by_css_selector(".fp-text > b:nth-child(1)").text)
        PAGE += 1
        
    return lost_item

if __name__ == "__main__":
    driver = webdriver.Firefox(executable_path="/Users/clytie/Documents/研究生/文本挖掘/JD/code/geckodriver")
    driver.get("https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8")
    driver.maximize_window()            
    time.sleep(5)
    print "开始爬取"
    print "=" * 50
    
    lost_item = get_phone(driver)
    
    print "爬取结束"
    
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
                                        
    

