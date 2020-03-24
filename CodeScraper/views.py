from django.shortcuts import render, redirect
import requests, ssl, urllib, traceback
from bs4 import BeautifulSoup
from requests import get

# Create your views here.

code_list = []

def index(request):
  code_list = []
  return render(request, 'index.html')

def process(request):
  base_url = "https://www.google.co.kr/search"
  q_id=request.POST['oj_url'].split('/')[-1]
  lang=request.POST['lang']
  searching = f"백준 {q_id} {lang}"

  values={
    'q':searching,
    'oq':searching,
    'aqs':'chrome..69i57.35694j0j7',
    'sourceid':'chrome',
    'ie':'UTF-8',
  }

  hdr={'User-Agent':'Mozilla/5.0'}

  querystring=urllib.parse.urlencode(values)
  req=urllib.request.Request(base_url+'?'+querystring, headers=hdr)
  context=ssl._create_unverified_context()
  try:
    res=urllib.request.urlopen(req, context=context)
  except:
    traceback.print_exc()

  soup=BeautifulSoup(res.read(), 'html.parser')
  #print(soup.prettify('utf-8'))
  targets = soup.find_all('a')[17:27]
  target_url_list=[]
  for target in targets:
    target_url_list.append('https://www.google.com'+target.get("href"))
  #print(target_url_list)
  #return redirect('result', lang=lang, q_id=q_id)
  codes_list = []
  for url in target_url_list:
    result = requests.get(url, headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'})
    result.encoding = "utf-8"
    soup = BeautifulSoup(result.content.decode("utf-8"), "html.parser")
    print("Scraping site url : "+url)
    if soup.find("div", {"class":"colorscripter-code"}):
      print("got colorscripter")
      codes_list.append(soup.find_all("div", {"class":"colorscripter-code"}))
    elif soup.find("div", {"class":"se_code"}):
      print("got __se_code_view")
      codes_list.append(soup.find_all("div", {"class":"se_code"}))
    elif soup.find("table", {"class":"highlight"}):
      print("got highlightjs")
      codes_list.append(soup.find_all("table", {"class":"highlight"}))
#왠진 모르겠지만 se_code랑 highlightjs가 포함된 html들은 제대로 긁혀 오지가 않네요..
    elif soup.find("code"):
      print("got code")
      codes_list.append(soup.find_all("code"))
    else:
      continue
  for codes in codes_list:
    #여기를 lstrip하면 왼쪽 공백이 사라질 줄 알았는데ㅜㅜ
    code_list.append(str(codes)[1:-1].lstrip())
    print(type(str(codes)))
  return redirect('result', lang=lang, q_id=q_id)
  #return redirect(f'result/{lang}/{q_id}')

def result(request, lang, q_id):
  #print(code_list)
  return render(request, 'result.html', {'q_id':q_id, 'lang':lang, 'code_list':code_list})
