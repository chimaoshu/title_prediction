import requests
from bs4 import BeautifulSoup
import time
import string
import json
import hashlib
from urllib.parse import quote
import random


# 调用api，对公文标题进行分词


class getAPI():

    @staticmethod
    def curlmd5(src):
        m = hashlib.md5(src.encode('UTF-8'))

        # 将得到的MD5值所有字符转换成大写
        return m.hexdigest().upper()

    @staticmethod
    def get_params(text):

        # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效） 
        t = time.time()
        time_stamp = str(int(t))

        # 请求随机字符串，用于保证签名不可预测  
        nonce_str = ''.join(random.sample(
            string.ascii_letters + string.digits, 10))

        # 腾讯云可以免费开通使用，但是有并发量限制  
        app_id = '2131825293'
        app_key = 'oV8RSUibqk37pcLg'
        params = {
            'app_id': app_id,
            'time_stamp': time_stamp,
            'nonce_str': nonce_str,
            'text': text
        }

        sign_before = ''

        # 要对key排序再拼接
        for key in sorted(params):
            # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。
            sign_before += '{}={}&'.format(key, quote(params[key], safe=''))

        # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
        sign_before += 'app_key={}'.format(app_key)

        # 对字符串sign_before进行MD5运算，得到接口请求签名  
        sign = getAPI.curlmd5(sign_before)

        params['sign'] = sign

        return params

    @staticmethod
    def get_content(text):

        # 去掉特殊字符
        text = text.replace(' ', '').replace('~', '')

        print('输入内容：' + text)

        # 由于使用的是免费的api接口，需要保证一定的访问时间差，采用这种方法保证时间间隔
        while True:
            with open('1_原始数据获取和处理\\api_timestamp.txt', 'a+', encoding='utf-8') as f:
                last_timestamp = f.read()

                if last_timestamp == '':
                    f.seek(0, 0)
                    f.truncate()
                    f.write(str(time.time()))
                    break

                if time.time() - float(last_timestamp) < 1:
                    time.sleep(2)

                else:
                    f.seek(0, 0)
                    f.truncate()
                    f.write(str(time.time()))
                    break

        # API地址
        url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_wordpos"

        # 获取请求参数  
        try:
            text = text.replace('\u2022', '').replace('\ufffd', '').replace('・', '').encode('gbk')
        except:

            for each_char in text:
                try:
                    each_char.encode('gbk')
                except:
                    text = text.replace(each_char, '')
            else:
                try:
                    text = text.encode('gbk')
                except:
                    return 0

        payload = getAPI.get_params(text)

        while True:
            try:
                respond_dict = requests.post(url, data=payload).json()
                break
            except:
                time.sleep(3)

        if respond_dict['ret'] != 0:

            print('调用接口失败，原因是%s' % respond_dict['msg'])
            return 0

        else:
            # 屏蔽掉一些没用的词
            fittered_list = [0, 1, 4, 5, 7, 8, 9, 15, 23, 24,
                             25, 26, 27, 28, 29, 30, 34, 35, 49, 50, 51, 52, 55]
            respond_dict = respond_dict['data']['mix_tokens']

            result_list = []
            for x in respond_dict:
                if not x['pos_code'] in fittered_list:
                    result_list.append(x['word'])
            else:
                del x

            print(result_list)

        return (result_list)


def get_data(year):
    """
    从学校官网获取公文和对应的点击量
    """
    print(year, '年')

    with open('1_原始数据获取和处理\\1_演示_2020年新数据.json', 'r', encoding='utf-8') as f:
        data_list = json.loads(f.read())

    if year == 2021:
        keyword = ''
    else:
        keyword = '通知'

    respond_list = requests.post(
        url='https://www1.szu.edu.cn/board/infolist.asp?',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20120101 Firefox/33.0'},
        proxies={},
        data={'dayy': str(year), 'from_username': '',
              'keyword': keyword.encode('gbk'), 'searchb1': '%CB%D1%CB%F7'}
    )

    respond_list.encoding = 'gbk'

    soup = BeautifulSoup(respond_list.text, "html5lib")

    try:
        father_tag = soup.find_all("table")[8].find_all("tr")[2:]
    except(IndexError):
        print('网络出错，检查代理')

    for content in father_tag:

        order = len(data_list)
        try:

            td = (content.find_all("td"))
            title = content.find("a", class_="fontcolor3").text
            click_times = int(td[6].text)

            if click_times >= 2000:
                continue

            keyword_list = getAPI.get_content(title)

            # 如果为空.跳过
            if not keyword_list:
                print('跳过')
                continue

            order += 1
            if not data_list.__contains__(str(order)):
                data_list[str(order)] = {
                    "keyword": keyword_list,
                    "click_times": click_times
                }

        except:
            print('出错，跳过')

    with open('1_原始数据获取和处理\\1_演示_2020年新数据.json', 'r+', encoding='utf-8') as f:
        # with open('数据处理\\训练数据获取与处理\\3_training_data.json', 'r+', encoding='utf-8') as f:
        f.seek(0, 0)
        f.truncate()
        f.write(
            json.dumps(
                data_list,
                ensure_ascii=False
            )
        )


if __name__ == "__main__":
    """
    这个爬虫的目的是从学校的官网爬取公文标题和对应的点击量
    """

    # get_data(2019)
    get_data(2020)
