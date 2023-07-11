# -*- coding: utf-8 -*-
# from socket import socket, timeout
import urllib
from urllib import request
import urllib.error
# import sqlite3
import random
import time
import re
import eventlet
# import xlwt
import os
import requests # 用于发送网络请求
from bs4 import BeautifulSoup # 用于解析HTML文档，提取其中的信息

from urllib3.exceptions import InsecureRequestWarning # 用于处理网络请求时的安全警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # 关闭因使用了不安全的http请求而产生的警告

def pmc_down(parameter):
    eventlet.monkey_patch()
    downpara="pmc/articles/"+parameter+"/pdf/main.pdf"
    #openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
    baseurl = "https://www.ncbi.nlm.nih.gov/"
    url=baseurl+downpara
    timeout_flag=0
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    try:
        with eventlet.Timeout(180,True):
            response = urllib.request.urlopen(request, timeout=60)
            html = response.read()
            print("%s.pdf" % parameter, "从目标站获取pdf数据成功")
            return html
    except urllib.error.URLError as e:
        if hasattr(e, "code"):  # 判断e这个对象里面是否包含code这个属性
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        timeout_flag=1
        return timeout_flag
    except eventlet.timeout.Timeout:
        timeout_flag=1
        print("下载目标数据超时")
        return timeout_flag
    except:
        print("%s.pdf"%parameter,"从目标站获取pdf数据失败")

def pmc_save(html,PMCID,name, out_dir):
    # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了
    try:
        name=re.sub(r'[< > / \\ | : " * ?]',' ',name)
        #需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
        savepath=f"{out_dir}/{name}.pdf"
        file=open(savepath,'wb')
        print("open success")
        file.write(html)
        file.close()
        # print("%s.pdf"%name,"文件写入到output下成功")
        print("pdf文件写入成功,文件ID为 %s"%PMCID,f"保存路径为{out_dir}")
    except:
        print("pdf文件写入失败,文件ID为 %s"%PMCID,"文件写入失败,检查路径")

def pmc_get(df, out_dir):
    n = 0
    for index, row in df[df['PMC'].notna()].iterrows():
        n += 1
        html = pmc_down(row["PMC"])
        pmc_save(html, row["PMC"], row["Title"], out_dir)
    
    print(f"PMC文献库下载完成{n}篇文献！\n")
    
# def scihub_get(df, out_dir):
    # print("剩余文献需要从scihub中下载，由于下载速度过慢，此处不进行")
    # nan_rows = df[df['PMC'].isna()]
    # nan_rows = nan_rows[nan_rows['DOI']!= "暂时缺失，请手动查询"]
    # nan_rows['DOI'].to_csv(f'{out_dir}/doi.txt', header=False, index=False)
    # print("没有PMC的文献doi已经存入doi.txt\n")
    # print("请运行以下代码完成下载\n")
    # print(f"scihub-cn -i {out_dir}/doi.txt --doi")
    
def scihub_get(df, download):
    for index, row in df[df['PMC'].isna()].iterrows():
        doi = row["DOI"]
        web = f"https://sci-hub.se/{doi}"
        try:
            response = requests.get(web, verify=False)
            content = response.content
            soup = BeautifulSoup(content, "html.parser")
        except RecursionError:
            print(f'网络原因，{doi}无法访问')
            continue
        try:
            button = soup.find('button') #找到第一个button标签
            onclick_text = button.get('onclick') #获取button标签的onclick属性的值
            link = onclick_text.replace("location.href='", '').replace("'", '') #从onclick属性的值中提取链接
            url = f'https://sci-hub.se{link}'
            df.loc[index, 'PMC'] = url
            print(f'{doi}的scihub链接已经补充到PMC列中')
        except AttributeError:
            print(f'{doi}没有获得相应的下载链接。')
            continue
    df.to_excel(download, index=False)
    print("scihub下载链接提取完成，已存放至PMC列！\n")
