# import csv # 用于读写csv文件
import requests # 用于发送网络请求
from bs4 import BeautifulSoup # 用于解析HTML文档，提取其中的信息
import re # 用于使用正则表达式匹配和处理字符串
import calendar # 用于处理日期相关的操作
from urllib3.exceptions import InsecureRequestWarning # 用于处理网络请求时的安全警告
# import json
import pandas as pd

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # 关闭因使用了不安全的http请求而产生的警告

# 定义日期转换
def convert_date(date_string):
    match = re.search(r"(\d{4})(?: (\w{3})(?: (\d{1,2}))?)?", date_string)
    if match:
        year, month, day = match.groups()
        if month:
            month_dict = {v: k for k, v in enumerate(calendar.month_abbr)}
            month = month_dict[month]
            day = day if day else "01"
            return f"{year}-{month:02d}-{day.zfill(2)}"
        else:
            return year
    else:
        return "Unknown"

# 定义信息提取
def extract_articles(url, page_start=1):
    data = []
    page = page_start
    while True:
        response = requests.get(url, params={"page": page}, verify=False)
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        articles = soup.find_all("div", {"class": "short-view"})
        abstracts = soup.find_all("div", {"class": "abstract"})
        if len(articles) == 0:
            break
        for count, (article, abstract) in  enumerate(zip(articles, abstracts), 1):
            title = article.find("h1", {"class": "heading-title"}).text.strip()
            journal_abbreviation = article.find("span", {"class": "citation-journal"}).text.strip()
            if journal_abbreviation.endswith('.'):
                journal_abbreviation = journal_abbreviation[:-1]
            publication_date = article.find("span", {"class": "cit"}).text.split(";")[0].strip()
            publication_date = convert_date(publication_date)
            try:
                doi = article.find("span", {"class": "citation-doi"}).text.split(":")[1].strip()
                if doi.endswith('.'):
                    doi = doi[:-1]
            except AttributeError:
                doi = '暂时缺失，请手动查询'
            try:
                pmid = article.find("strong", {"class": "current-id"}).text.strip()
                pubmed_web = f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'
            except AttributeError:
                pmid = '暂时缺失，请手动查询'
                pubmed_web = ''
            try:
                pmc = article.find("a", {"data-ga-action": "PMCID"}).text.strip()
            except AttributeError:
                pmc = ''
            abstr = abstract.text.strip()
            abstr = re.sub(r"\n\s+", "\n", abstr)
            # print("抓取完第",count,"篇文献:", title)
            data.append([title, journal_abbreviation, publication_date, pmid, pubmed_web, doi, pmc, abstr])
        print(f'PubMed: Completed page {page}')
        page += 1
    df = pd.DataFrame(data, columns=["Title", "Journal Abbreviation", "Publication Date", "PMID", "Pubmed Web","DOI", "PMC","Abstract"])
    return df

# 期刊信息匹配
def merge_dataframes(df):
    # 读取J_Medline.csv文件并创建DataFrame，只保留MedAbbr和JournalTitle两列
    journal_df = pd.read_csv('../data/J_Medline.csv', usecols=['MedAbbr', 'JournalTitle'])

    # 合并DataFrame，根据Journal Abbreviation和MedAbbr进行连接
    df = df.merge(journal_df, left_on='Journal Abbreviation', right_on='MedAbbr', how='left')

    # 删除多余的列，只保留JournalTitle列
    df.drop(columns=['MedAbbr'], inplace=True)

    # 读取文件
    df_jcr = pd.read_csv('../data/2022-2023IF.csv', usecols=['journal_name', 'category',"if_2023", 'if_2022'])
    regex_pattern = r"\((Q[1-4])\)$"

    # 提取括号中的内容，如果匹配成功则提取，否则填充为"NaN"
    df_jcr['category'] = df_jcr['category'].str.extract(regex_pattern).fillna("NaN")

    # 将要匹配的列转换为小写并且删除逗号和点，删除单词 "The"，并且将 "and" 替换为 "&"
    df['JournalTitle_lower'] = df['JournalTitle'].str.lower().str.replace('[.,]', '', regex=True).str.replace(' the ', ' ').str.replace(' and ', ' & ')
    df_jcr['journal_name_lower'] = df_jcr['journal_name'].str.lower().str.replace('[.,]', '', regex=True).str.replace(' the ', ' ').str.replace(' and ', ' & ')

    # 合并DataFrame，根据JournalTitle_lower和Journal Name_lower进行连接
    df = df.merge(df_jcr, left_on='JournalTitle_lower', right_on='journal_name_lower', how='left')

    # 删除多余的列
    df.drop(columns=['JournalTitle_lower', 'journal_name_lower', 'journal_name'], inplace=True)

    return df