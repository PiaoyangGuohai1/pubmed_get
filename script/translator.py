import requests # 用于发送网络请求
import time
import random
import json
from hashlib import md5

# 定义翻译函数
def translate_text(query, appid, appkey, apispeed):
    # Set your own appid/appkey.
    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang =  'zh'
    # 构建url
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    # 提取翻译结果
    try:
        translations = [item['dst'] for item in result['trans_result']]
        time.sleep(1/apispeed)  # 在每次翻译后暂停1秒
    except KeyError:
        print("请检查api的准确性，并保证有足够的余额。")
        raise RuntimeError("Translation failed")  # 引发新的异常
    return '\n '.join(translations)
    
# 翻译
def translate_df(df, appid, appkey, apispeed):
    # 检查是否提供了appid和appkey
    if not appid or not appkey:
        raise ValueError("请提供api的appid和appkey，具体请前往百度翻译进行注册查看。")

    print("正在Q1期刊的翻译标题和摘要，请稍等。。。\n")
    
    # 对于 'Category' 为 'Q1' 的行，对 'Title' 列进行翻译
    for index, row in df[df['category'] == "Q1"].iterrows():
        try:
            text_t = row['Title']
            translated_text_t = translate_text(text_t, appid, appkey, apispeed)
            df.loc[index, 'Title_translated'] = translated_text_t
            
            text_a = row['Abstract']
            translated_text_a = translate_text(text_a, appid, appkey, apispeed)
            df.loc[index, 'Abstract_translated'] = translated_text_a
        except RuntimeError:
            break  # 异常出现时，停止循环
                
    print("翻译结束！\n")
    return df