from flask import Flask, render_template, send_from_directory, redirect
from requests.utils import requote_uri
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import requests
import json
import os

with open("setting.json") as setting_file:
    setting_json = json.load(setting_file)

app = Flask(__name__)
naverheader = {'X-Naver-Client-Id': '', 'X-Naver-Client-Secret': ''}

@app.route('/')
def main_page():
    data = '''
        <div id="searchbox">
            <img src="SearchWeb.png" width="500px" id="mainimg">
        	<div id="searchform">
				<div id="searchinputbox">
                    <input id="searchinput" name="search" placeholder="원하는 검색어를 입력하세요." type="search" onkeydown="enterSearch();">
                    <button method="post" id="searchbutton" type="submit" formaction="/search" onclick="gopageSearch();">검색</button>
                    <button type="submit" id="helpbutton" onclick="helpdisplayfold();">도움말</button>
                </div>
            </div>
        </div>
        <div id="helpbox" style="display: none;">
            <span id="title">Help</span><span id="closebutton" style="float: right; cursor: pointer;" onclick="helpdisplayfoldclose();">X</span>
            <br><br>
            SearchWeb은 구글과 네이버의 검색어를 한 눈에 볼 수 있는 편리한 검색 엔진입니다. 깔끔한 디자인과 정확한 정보로 편한 검색 생활을 누려보세요.
            <br><br>
            첫 화면에 있는 검색창에 원하는 검색어를 입력한 뒤, Enter 키나 검색 버튼을 누르면 검색이 됩니다. 검색 결과는 Google과 NAVER의 순서대로 표시됩니다. 오른쪽에는 급상승 검색어가 존재하여 많은 사람들이 찾는 다양한 소식을 검색 결과 옆에서 바로 확인할 수 있습니다.
            <br><br>
            <span style="color: lightgray">
            Google은 Google LLC.의 등록상표입니다.<br>NAVER은 NAVER Corp.의 등록상표입니다.<br><br>SearchWeb은 Google이나 NAVER에서 운영하는 사이트가 아닙니다.
            <br><br>
            ⓒ 2020. Jung-Hyuk Kwon</span>
        </div>
    '''
    
    return render_template('index.html', data=data, title="SearchWeb")

@app.route('/search')
@app.route('/search/')
def redirectm():
    return redirect('/')

@app.route('/search/<name>')
def find_page(name):
    data = ''
    normalname = name
    name = requote_uri(name)
    naverurl = 'https://openapi.naver.com/v1/search/blog.json?query=' + name
    googleurl = "https://google.co.kr/search?q=" + name + "&lr=lang_ko"
    listurl = 'https://datalab.naver.com/keyword/realtimeList.naver'
    
    naverreq = requests.get(naverurl, headers=naverheader)
    googlereq = requests.get(googleurl, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.107.16 Safari/537.36"})
    
    naverresult = json.loads(naverreq.text)
    googleresult = googlereq.text
    naverlen = len(naverresult['items'])

    res = requests.get(listurl, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.107.16 Safari/537.36"})
    soup = BeautifulSoup(res.content, 'html.parser')
    item = soup.select('span.item_title')
    
    soup = BeautifulSoup(googleresult, 'html.parser')
    googletitle = soup.select('h3 > span')
    googledes = soup.select('div.IsZvec > div > span', limit=len(googletitle))
    googlelink = soup.select('div.yuRUbf > a', limit=len(googletitle))
    
    data = '''
            <div id="searchinfo">
                <br>
                <div>
                    <a href="/"><img src="/SearchWeb.png" width="300px"></a>
                    <div id="searchform">
                        <input id="searchinput" name="search" placeholder="원하는 검색어를 입력하세요." style="width: 718px;" onkeydown="enterSearch();">
                        <button method="post" id="searchbutton" type="submit" formaction="/search" onclick="gopageSearch();">검색</button>
                        <button type="submit" id="helpbutton" onclick="helpdisplayfold();">도움말</button>
                    </div>
                </div>
                <br>
                <br>
                <div id="searchside">
                    <span id="title">급상승 검색어</span><br>
                '''
                
    for item in item[0:10]:
        data += '<a href="/search/' + item.get_text() + '" id="listdata">' + item.get_text() + '</a>'
        
    data += '''
        </div>
        '''
    
    naverdata = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    
    for i in range(naverlen):
        title = naverresult["items"][i]["title"]
        link = naverresult["items"][i]["link"]
        des = naverresult["items"][i]["description"]
        date = naverresult["items"][i]["postdate"]
        
        naverdata[i] = '''
            <div id="result">
                <a href="''' + link + '''" id="title">''' + title + '''</a> - <span id="date">''' + date + '''</span>
                <br>
                <br>
                <span id="des">''' + des + '''</span>
                <br>
                <br>
                <span style="color: #03c75a">NAVER</span>
            </div>
        '''
        
    i = 0
        
    for googletitle, googledes, googlelink in zip(googletitle, googledes, googlelink):
        title = googletitle.text
        des = googledes.text
        link = googlelink.text
        if not i > naverlen:
            i += 1
        
        data += '''
                <div id="result">
                    <a href="''' + link + '''" id="title">''' + title + '''</a>
                    <br>
                    <br>
                    <span id="des">''' + des + '''</span>
                    <br>
                    <br>
                    <span style="color:#4285F4">G</span><span style="color:#EA4335">o</span><span style="color:#FBBC05">o</span><span style="color:#4285F4">g</span><span style="color:#34A853">l</span><span style="color:#EA4335">e</span>
                </div>
        '''
        
        data += naverdata[i]
        
    data += '''
                </div>
                <div id="helpbox" style="display: none;">
                    <span id="title">Help</span><span id="closebutton" style="float: right; cursor: pointer;" onclick="helpdisplayfoldclose();">X</span>
                    <br><br>
                    SearchWeb은 구글과 네이버의 검색어를 한 눈에 볼 수 있는 편리한 검색 엔진입니다. 깔끔한 디자인과 정확한 정보로 편한 검색 생활을 누려보세요.
                    <br><br>
                    첫 화면에 있는 검색창에 원하는 검색어를 입력한 뒤, Enter 키나 검색 버튼을 누르면 검색이 됩니다. 검색 결과는 Google과 NAVER의 순서대로 표시됩니다. 오른쪽에는 급상승 검색어가 존재하여 많은 사람들이 찾는 다양한 소식을 검색 결과 옆에서 바로 확인할 수 있습니다.
                    <br><br>
                    <span style="color: lightgray">
                    Google은 Google Inc.의 등록상표입니다. NAVER은 NAVER Corp.의 등록상표입니다. 이 사이트는 Google이나 NAVER에서 운영하는 사이트가 아닙니다.
                    <br><br>
                    ⓒ 2020. Jung-Hyuk Kwon</span>
                </div>
            '''
    
    return render_template('index.html', data=data, title='"' + normalname + '" - SearchWeb')
    
@app.route('/<name>')
def main_file(name):
    if os.path.exists(name):
        return send_from_directory('./', name)

if __name__ == '__main__':
    app.run(host=setting_json["host"], port=setting_json["port"])