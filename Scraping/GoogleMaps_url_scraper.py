#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 操作 browser 的 API
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# 處理逾時的例外工具
from selenium.common.exceptions import TimeoutException

# 等待某個元素的出現
from selenium.webdriver.support.ui import WebDriverWait

# 期待元素出現並執行下一個指令
from selenium.webdriver.support import expected_conditions as EC

# 透過什麼方式選取元素
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# 強制等待
from time import sleep

# 反爬蟲
# import undetected_chromedriver as uc

# 執行 command 的時候用的
import os

# 整理 json 使用的工具
import json

#計算程式執行的時間
import time

# 平行任務處理
from concurrent.futures import ThreadPoolExecutor as tpe

# regex
import re

# 檔案需轉成csv
import pandas as pd

# 啟動瀏覽器工具的選項
my_options = webdriver.ChromeOptions()

my_options.add_argument("--start-maximized") # 視窗最大化
my_options.add_argument("--incognito") # 無痕
my_options.add_argument("--disable-popup-blocking") # 禁用彈出攔截
my_options.add_argument("--disable-notifiactions") # 關閉推波通知
my_options.add_argument("--lang=zh-TW") # 設定為繁體中文
my_options.add_argument("--headless")
# my_options.add_argument("--user-agent="+ua.random)

# 建立儲存檔案的資料夾
folderPath = "景點"
if os.path.exists(folderPath) != True:    
    os.makedirs(folderPath)

# 每搜尋一次計數器+1
index = 0


# In[ ]:


def page_link(link):
    
    global index
    
    # 使用 Chrome 的 WebDriver
    driver = webdriver.Chrome(
        options = my_options,
        service = Service(ChromeDriverManager().install())
    )
    
    # GoogleMap網址
    url = "https://www.google.com.tw/maps/@23.546162,120.6402133,8z?hl=zh-TW"
    
    driver.get(url)
    
    sleep(1)
    
    # 計算每跑一次跑多久
    start = time.time()
        
    # 輸入關鍵字搜尋
    driver.find_element(
        By.CSS_SELECTOR,
        "input#searchboxinput"
    ).send_keys(link)
    
    # 按下搜尋按鈕
    driver.find_element(
        By.CSS_SELECTOR,
        "button#searchbox-searchbutton"
    ).click()
        
    sleep (3)
        
    # 找搜尋元素結果的div
    focus = driver.find_elements(
        By.CSS_SELECTOR,
        "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd"
    )[1]

    offset = 0
    innerHeight = 0
    count = 0  # 累計無效滾動次數
    limit = 5  # 最大無效滾動次數
    Flag = True
    counter = 0
        
    # 開始滾輪找到最底部
    while Flag:
            
        try:
            # 等待底部元素出現
            WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located( 
                    (By.CSS_SELECTOR, "span.HlvSq") 
                )
            )
            
            break
            
        except TimeoutException:

           # offset: 拉槓到頁面頂端的距離
            offset = driver.execute_script('return arguments[0].scrollTop', focus)

            # 執行js指令捲動頁面
            driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', focus)
            
            # innerHeight: 頁面高度 = 拉槓到頁面頂端的距離
            innerHeight = driver.execute_script('return arguments[0].scrollHeight = arguments[0].scrollTop', focus)
            
            # 如果「拉槓到頁面頂端的距離」(offset)等於「頁面高度 = 拉槓到頁面頂端的距離」(innerHeight)，代表搜尋可能逾時
            if offset == innerHeight:
                count += 1                
              
            # 計數器等於限制數則搜尋確實逾時了,需重新整理並搜尋
            if count == limit:
                
                counter+=1
                
                print(f"{link}需重新整理,搜尋逾時,本次刷新第{counter}次")
                
                # 網頁重新整理
                driver.execute_script('window.location.replace(window.location.href)')
                
                # 重新搜尋
                driver.find_element(
                    By.CSS_SELECTOR,
                    "button#searchbox-searchbutton"
                 ).click()
                
                sleep(3)

                # 找搜尋結果的div
                focus = driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd"
                    )[1]

                # 重新定義需要的變數
                offset = 0
                innerHeight = 0
                count = 0  # 累計無效滾動次數
                
            sleep(1)
            
    # 尋找所有元素的href    
    href_ = driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-js-log-root] a[aria-label]"
    )
    
    
    # 放xx區裡的xx路餐廳的網址lict
    listUrl=[]
    counter = 0 

    # 把所有href加進listUrl裡
    for href in href_:        
        listUrl.append({
       
            "href":href.get_attribute("href")
        })      
        counter+=1
    
    # 把餐廳網址list先轉成dataframe再存成csv        
    df = pd.DataFrame(listUrl)
    df.to_csv(f'{folderPath}/{folderPath}.csv',mode='a', header=False, index=False)
    
    # 清除搜尋的關鍵字
    driver.find_element(
        By.CSS_SELECTOR,
        "input#searchboxinput"
    ).clear()   
    
    # 每搜尋成功並寫入就計數器+1
    index+=1
    
    end = time.time()
    print(f'第{index}筆[{link}],總共有:{counter}筆,已寫入完成,process_time：%f 秒'% (end - start))
    
    driver.quit()

    # 每條(街or路)的全部restaurantType都抓完,則提示已完成全(街or路)抓取,,總共restaurantType有26種
#     if index%26 == 0:
#         regex01 = r'.+(街|路)'
#         string01 = link
#         match01 = re.search(regex01, string01)
#         print(f'注意!!!{match01[0]}:已全數寫入完成\n')


# In[ ]:


def multiprocess():
    
    district = ["中正區","松山","中山","文山","內湖","南港","士林","大同","北投","萬華","大安","信義"] 
    
    attractions = ["紀念公園","歷史地標","旅遊景點","歷史建築","夜景"]
#     roadNames = ["三元街","中山北路一段","中山南路","中華路一段","中華路二段","丹陽街","仁愛路一段","仁愛路二段","信義路一段","信義路二段","信陽街","八德路一段","公園路","凱達格蘭大道","北平東路","北平西路","南昌路一段","南昌路二段","南海路","南陽街","博愛路","同安街","和平西路一段","和平西路二段","大埔街","天津街","寧波東街","寧波西街","寶慶路","市民大道一段","市民大道二段","市民大道三段","師大路","常德街","廈門街","廣州街","延平南路","徐州路","忠孝東路一段","忠孝東路二段","忠孝西路一段","思源街","惠安街","愛國東路","愛國西路","懷寧街","新生南路一段","晉江街","杭州北路","杭州南路一段","杭州南路二段","林森北路","林森南路","桃源街","武昌街一段","水源路","永春街","永綏街","汀州路一段","汀州路二段","汀州路三段","沅陵街","泉州街","泰安街","湖口街","漢口街一段","潮州街","濟南路一段","濟南路二段","牯嶺街","福州街","秀山街","紹興北街","紹興南街","羅斯福路一段","羅斯福路二段","羅斯福路三段","羅斯福路四段","臨沂街","自強市場第三棟","莒光路","衡陽路","襄陽路","西藏路","許昌街","詔安街","貴陽街一段","辛亥路一段","連雲街","酉陽街","重慶南路一段","重慶南路二段","重慶南路三段","金山北路","金山南路一段","金華街","金門街","銅山街","鎮江街","長沙街一段","開封街一段","青島東路","青島西路","館前路","齊東街"]
    # 26種
#     restaurantType = ["火鍋","拉麵料理","日式料理","美國菜","義大利菜","法式料理","中國菜","台灣菜","韓國菜","德國菜","地中海料理","印度料理","越南菜","港式","泰國菜","南洋","素食","鐵板燒","餐酒館","咖啡廳","熱炒店","早午餐","甜點店","燒肉","海鮮餐廳","牛排"]

    drt = []
    
#     for road in roadNames:
#         for type_ in restaurantType:
#             keyword = f'{district}{road}{type_}' 
#             # 平行運算x2,
#             drt.append(keyword)
    for district in district:
        for type_ in attractions:
            keyword = f'{district}{type_}' 
            # 平行運算x2,
            drt.append(keyword)
    
    with tpe(max_workers=5) as executor:
        executor.map(page_link,drt) # 執行page_link涵式,drt是涵式需要的變數
      


# In[ ]:


if __name__=="__main__":
    time1 = time.time()
    multiprocess()
    print(f'總共{index}筆,總花費時間: {time.time() - time1}')

