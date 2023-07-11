# Author: Long Xinyang
# Date: 2023-07-10

# 1、输入url即可进行爬虫，但url要求是abstract格式，在pubmed中进行选择，然后复制网址
# 2、可以爬"Title", "Journal Abbreviation", "Publication Date", "PMID", "Pubmed Web", "DOI", "Abstract"信息
# 3、针对期刊，添加了JCR分区和2022年及2023年影响因子
# 4、调用--translate即可通过百度翻译api进行翻译，但需要提供--appid 和 --appkey 
# 5、当前调用api的速度是1秒进行1次访问（标准用户只能进行一次，高级用户最多可以进行10次），如果你是高级用户，可以修改apispeed参数。

# 参数说明
# 使用python pubmed_get.py -h查看帮助文档

# 示例运行
# url="https://pubmed.ncbi.nlm.nih.gov/?term=gut-kidney+axis+AND+PA&filter=years.2021-2023&format=abstract&size=20"
# 不翻译
# python pubmed_get.py --url $url
# 翻译标准用户
# python pubmed_get.py --url $url --translate --appid XXXXX --appkey XXXXX
# 翻译高级用户
# python pubmed_get.py --url $url --translate --appid XXXXX --appkey XXXXX --apispeed 10

# 安装所需要的包 pip install -r requirement.txt
import argparse
import re # 用于使用正则表达式匹配和处理字符串
import os
import pandas as pd
import datetime
import csv
import random
from pubmed_get import *
from translator import * 
from prepare import *
from pdf_download import *

def main(url, translate, appid, appkey, apispeed, download, output):
    if url:
        if "format=abstract" not in url:
            print("URL format is incorrect. Please switch to abstract URL format.")
            return
        if not output:
            rd=random.randint(1000,9999)
            output=f'project_{rd}'
        out_dir = f"../output/{output}"
        os.makedirs(out_dir)
        print(f"结果将存放在文件夹{out_dir}")
        
        # 检查下载J_Medline文件
        J_Med_download()
        
        # 构造输出
        # url="https://pubmed.ncbi.nlm.nih.gov/?term=gut-kidney+axis+AND+PA&filter=years.2021-2023&format=abstract&size=20"
        today=datetime.date.today()
        formatted_today=today.strftime('%y%m%d')

        keywords = re.search(r"term=(.*)", url).group(1)
        keywords = re.sub(r"\d+", "", keywords)
        keywords = re.sub(r"[^\w\s]", "", keywords).replace(" ", "_")

        xlsx_name = f"PubMed_{keywords}.xlsx"
        xlsx_path = f"{out_dir}/{xlsx_name}"
        
        # 提取文献信息
        df = extract_articles(url)
        
        # 期刊信息匹配
        df = merge_dataframes(df)
        
        # 翻译
        if translate:
            df = translate_df(df, appid, appkey, apispeed)
        
        # 输出合并后的DataFrame
        df.to_excel(xlsx_path, index=False)
                    
    
    # 从PMC下载文件
    if download:
        out_dir = os.path.dirname(download)
        df = pd.read_excel(download)
        
        print("从PMC数据库下载文献。。。。")
        pmc_get(df, out_dir)
        
        #print("剩余文献需要从scihub中下载，由于下载速度过慢，此处不进行")
        #print("此处只提取下载链接，到df的PMC列中")
        #scihub_get(df, download)
        
    
    
    print("程序结束!")
    
    

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-u', '--url', type=str, help='The web URL to be processed.')
    parser.add_argument('-t', '--translate', action='store_true', help='Whether to translate the text.')
    parser.add_argument('--appid', type=str, help='The appid for translation.')
    parser.add_argument('--appkey', type=str, help='The appkey for translation.')
    parser.add_argument('--apispeed', type=float, default=1, help='api call frequency, the default value is 1 (once call per second). If you are a senior user, set it to 10.')
    parser.add_argument('-o','--output', type=str, help='which floder you want to save the result.')
    
    
    parser.add_argument('-d' ,'--download', type=str, help='which file you want to download.')
    
    args = parser.parse_args()
    main(args.url, args.translate, args.appid, args.appkey, args.apispeed, args.download, args.output)