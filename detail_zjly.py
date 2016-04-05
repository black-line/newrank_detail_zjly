#!/usr/bin/env python3

import urllib.request
import urllib.parse
import http.cookiejar
import json
import datetime
import sqlite3
import hashlib


def get_content():

    url_xhr = "http://www.newrank.cn/xdnphb/data/getAccountArticle"
    req = urllib.request.Request(url_xhr)

    # deal with headers
    ori_headers = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
#        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control':'max-age=0',
        'Content-Length':'90',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'DNT':'1',
        'Host':'www.newrank.cn',
        'Origin':'http://www.newrank.cn',
        'Proxy-Connection':'keep-alive',
        'Referer':'http://www.newrank.cn/public/info/detail.html?account=zjly_057112301',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }



    # set nance (0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f)9 of 16
    nonce = '012345678'

    # set xyz /*! xdnphb linux-grunt-xdnphb-copyright 2016-03-22 */
    appBase = '/xdnphb'
    urlBase = appBase+'/'
    xyz_str = urlBase + 'data/getAccountArticle?AppKey=joker&uuid=B06CF7ADA77947B013CAF3F9DDDB1E61'
    xyz = hashlib.md5((xyz_str+'&nonce='+nonce).encode()).hexdigest()

    # deal with form data
    form_data = urllib.parse.urlencode({
        'uuid':'B06CF7ADA77947B013CAF3F9DDDB1E61',
        'nonce':nonce,
        'xyz':xyz
    }).encode()

    # add headers to req
    for key, value in ori_headers.items():
        req.add_header(key, value)

    # deal with cookies
    cj = http.cookiejar.CookieJar()
    pro = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(pro)

    op = opener.open(req, form_data)
    data = op.read().decode("UTF-8")  # <class 'str'>

    ori_content = json.loads(data)
    inner_content = ori_content['value']
    print(inner_content)
    return inner_content


def store_to_db(content):

    commit_count = 0

    conn = sqlite3.connect('NEWRANK_hotByDay.db')

    cur = conn.cursor()
    # UID TEXT PRIMARY KEY NOT NULL
    cur.execute('''CREATE TABLE IF NOT EXISTS NEWRANK_hotByDay (ID TEXT PRIMARY KEY NOT NULL,
                                                       RANK_NAME TEXT NOT NULL,
                                                       AUTHOR TEXT,  --   jjjjjjjjjjjj
                                                       ACCOUNT TEXT,
                                                       TITLE TEXT,
                                                       URL TEXT,
                                                       IMAGE_URL TEXT,
                                                       CONTENT TEXT,
                                                       UID TEXT,
                                                       RANK_POSITION TEXT,
                                                       LIKE_COUNT TEXT,
                                                       CLICKS_COUNT TEXT,
                                                       PUBLIC_TIME TEXT,
                                                       RANK_DATE)''')

    L = []
    IDList = cur.execute("SELECT ID FROM NEWRANK_hotByDay")
    for row in IDList:
        L.append(row[0])

    for index in range(len(content)):
        uid_exist = 1  # uid existed
        if content[index]['id'] in L:
            uid_exist = 1
            break
        else:
            uid_exist = 0
        if len(cur.fetchall()) == 0:
            uid_exist = 0
        if uid_exist == 1:
            print("exist")
        else:
            cur.execute("INSERT INTO NEWRANK_hotByDay VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (content[index]['id'],
                         content[index]['rank_name'],   # 时事
                         content[index]['author'],
                         content[index]['account'],
                         content[index]['title'],
                         content[index]['url'],
                         content[index]['image_url'],
                         content[index]['content'],
                         content[index]['uid'],
                         content[index]['rank_position'],
                         content[index]['like_count'],
                         content[index]['clicks_count'],
                         content[index]['public_time'],
                         content[index]['rank_date']))
            commit_count += 1
    # Save (commit) the changes
    conn.commit()
    print("新增 "+str(commit_count)+" 条数据")
    conn.close()


def get_rownum_from_db():
    conn = sqlite3.connect('NEWRANK_hotByDay.db')
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM NEWRANK_hotByDay")
    total = cur.fetchone()
    conn.close()
    return total[0]


if __name__ == '__main__':
    content = get_content()
#    store_to_db(content)
#    rownum = get_rownum_from_db()
#    print('数据库中共有 '+str(rownum)+' 条数据')