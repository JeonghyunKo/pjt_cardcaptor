## project CardCaptor

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime 

try : 
    origin_df = pd.read_csv("ssg_card.csv", encoding = 'utf-8-sig')
except :
    origin_df = pd.DataFrame()


url = 'https://www.ssg.com/event/eventMain.ssg' 
r = requests.get(url)

if r.status_code == 200:
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

else : 
    print(r.status_code)

events = soup.find_all(class_ = 'evt_osmu_unit' )
event_ls = [] 
for event in events : 
    try : 
        name = event.find(class_ = 'eo_tit').find("strong").text
        if "카드" in name : 
            event_ls.append(event)
    except : 
        continue
        #하단 문화이벤트 영역이 공란일 경우 에러 발생시키기 때문에 try except 처리한다 

df = pd.DataFrame( {"date_start" : []
                    ,"date_end" : [] 
                    ,"card" : []
                    ,"descript" : []
                    ,"platform" : []
                    ,"detail_date" : []
                    ,"detail_card" : []
                    ,"detail_desc" : []
                    ,"detail_goods" : []
                    ,"detail_limit" : []
                    ,"update_dt" : []})

main_url = 'https://www.ssg.com'
update_dt = datetime.now()

for event in event_ls : 
    
    #기본정보
    date_total = event.find(class_ = 'eo_period').text.split(" - ")
    card = event.find(class_ = 'eo_tit').find("strong").text
    descript = event.find(class_ = 'desc1').text + " " + event.find(class_ = 'desc2').text
    platform = event.find(class_ = 'eo_mall').text.replace("\n", "")
    
    #링크타고 들어가서 얻는 디테일 
    #아니 왜 링크 유형이 제각각이야 
    event_url = event.find(href=True)["href"]
    if "https://" not in event_url : 
        second_url = main_url + event_url
    else : 
        second_url = event.find(href=True)["href"]
        
    r2 = requests.get(second_url)

    if r2.status_code == 200:
        html = r2.text
        soup = BeautifulSoup(html, 'html.parser')

    else : 
        print(r2.status_code)
        
    try : 
        details = soup.find(class_="ecard_info").find_all("li")
        for d in details : 

            item = d.find(class_="tit").text
            content = d.text.replace(d.find(class_="tit").text, "")

            if item == '행사기간' : 
                detail_date = content
            elif item == '대상카드' : 
                detail_card = content
            elif item == '행사내용' :
                detail_desc = content
            elif item == '대상상품' : 
                detail_goods = content
            else : 
                detail_limit = content
    except : 
        detail_date, detail_card, detail_desc, detail_goods, detail_limit = "", "", "", "", ""

    row = pd.DataFrame.from_dict( [{"date_start" : date_total[0]
                        ,"date_end" : date_total[1]
                        ,"card" : card
                        ,"descript" : descript
                        ,"platform" : platform
                        ,"detail_date" : detail_date
                        ,"detail_card" : detail_card
                        ,"detail_desc" : detail_desc
                        ,"detail_goods" : detail_goods
                        ,"detail_limit" : detail_limit
                        ,"update_dt" : update_dt}]) 
    
    
    df = pd.concat([df, row], ignore_index = True)
    df = pd.concat([origin_df, df], ignore_index = True)

#date = update_dt.strftime('%Y-%m-%d')
df = df.drop_duplicates(subset = ["date_start", "date_end", "card", "descript", "platform", "detail_date", "detail_card", "detail_desc", "detail_goods", "detail_limit"], keep = "last")
df.to_csv(f"./results/ssg_card_{update_dt}.csv", index = False, encoding = 'utf-8-sig')