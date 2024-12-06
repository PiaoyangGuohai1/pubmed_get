Author: Long Xinyang
Date: 2023-07-10

近期准备完成一些优化：
1. 补充2024年的影响因子
2. 补充JCR和中科院分区信息
3. 下载文献时添加序号编号，方便寻找需要手动下载的文献
4. 接入gpt api完成摘要翻译
5. 接入gpt api根据摘要信息完成所有论文的基础介绍


# 功能

1、输入url即可进行爬虫，但url要求是**abstract格式**，在pubmed中进行选择，然后复制网址

2、可以爬"Title", "Journal Abbreviation", "Publication Date", "PMID", "DOI", "Abstract"信息

3、针对期刊，添加了JCR分区和2022年及2023年影响因子

4、调用--translate即可通过百度翻译api进行翻译，但需要提供--appid 和 --appkey 

5、当前调用api的速度是1秒进行1次访问（标准用户只能进行一次，高级用户最多可以进行10次），如果你是高级用户，可以修改apispeed参数。

6、提供PMC下载（参考了[hiddenblue的Pubmedsoso](https://github.com/hiddenblue/Pubmedsoso)，表示感谢！）


![image.png|400](https://markdown-1300560293.cos.ap-guangzhou.myqcloud.com/markdown/20230710141748.png)


# 示例代码

## 配置环境

```shell
conda create -n pubmed python=3.10
conda activate pubmed
pip install -r requirement.txt
```

## 参数帮助

```shell
usage: main.py [-h] [-u URL] [-t] [--appid APPID] [--appkey APPKEY] [--apispeed APISPEED] [-o OUTPUT] [-d DOWNLOAD]

Process some integers.

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     The web URL to be processed.
  -t, --translate       Whether to translate the text.
  --appid APPID         The appid for translation.
  --appkey APPKEY       The appkey for translation.
  --apispeed APISPEED   api call frequency, the default value is 1 (once call per second). If you are a senior user, set it to 10.
  -o OUTPUT, --output OUTPUT
                        which floder you want to save the result.
  -d DOWNLOAD, --download DOWNLOAD
                        which file you want to download.
```

## 简单运行

```shell
cd ./script
url="https://pubmed.ncbi.nlm.nih.gov/?term=gut-kidney+axis&format=abstract&size=20"
python main.py -u $url -o 项目名
```

## API提供翻译标题和摘要

使用的是百度翻译api（文献量大时，会花费较多，此处默认设置只对Q1期刊翻译，大概300篇文献需要花费20元）

推荐使用excel-审阅-翻译，不要钱。

```shell
cd ./script
url="https://pubmed.ncbi.nlm.nih.gov/?term=gut-kidney+axis+AND+PA&filter=years.2021-2023&format=abstract&size=20"
# api高级开发者可设置apispeed为10
python main.py -u $url -o kidney -t --appid 你的id --appkey 你的key --apispeed 1 
```

## 下载PMC文献

自动下载到该xlsx文件所在的文件夹

```shell
cd ./script
python main.py -d "../output/kidney/PubMed_gutkidneyaxisformatabstractsize.xlsx"
```

# 结果预览

![image](https://github.com/PiaoyangGuohai1/pubmed_get/assets/53299096/7a4dc9d7-dd92-45a9-bf5b-950bdb21c7f1)

