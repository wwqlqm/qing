#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''工具类'''
__author__ = "wenxiaoning(wenxiaoning@gochinatv.com)"
__copyright__ = "Copyright of GoChinaTV (2017)."

from config.config import app
from config.config import logger
from config.config import LocalConfig
from urllib.parse import urlparse
from PIL import Image
import datetime
import hashlib
import re
import random
import time
import qrcode
import requests
import traceback
import pymysql.cursors
import io
import struct
import msgpack
import subprocess
from googletrans import Translator
from pypinyin import pinyin
from pypinyin import lazy_pinyin
from pypinyin import Style

RE_CHINESE = re.compile(u"[\u4e00-\u9fa5]+")  # 正则查找中文
RE_ENGLISH = re.compile(u"[A-Za-z]+")  # 正则查找英文
RE_MAC = re.compile(r'''
    (^([0-9A-F]{1,2}[-]){5}([0-9A-F]{1,2})$
    |^([0-9A-F]{1,2}[:]){5}([0-9A-F]{1,2})$
    |^([0-9A-F]{1,2}[.]){5}([0-9A-F]{1,2})$)
    ''', re.VERBOSE | re.IGNORECASE)

STR = [
    '0', '1', '2', '3', '4', '5',
    '6', '7', '8', '9', 'a', 'b',
    'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'j', 'k', 'l', 'm', 'n',
    'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
]
INTS = [
    '1', '2', '3', '4', '5',
    '6', '7', '8', '9'
]


def md5(str):
    """
    计算字符的md5摘要
    :param str:
    :return:
    """
    return hashlib.md5(str).hexdigest()

def sha1(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()

def sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def find_chinese(str):
    """
    查找字符串中中文集合
    :param str:
    :return:
    """
    return re.findall(RE_CHINESE, str)


def find_english(str):
    """
    查找字符串中的英文
    :param str:
    :return:
    """
    return re.findall(RE_ENGLISH, str)

def find_mac(s):
    """
    查找是否包含mac
    """
    return re.findall(RE_MAC, s)


def reduplicate(data):
    """
    去掉list中的重复值
    :param data:
    :return:
    """
    if not isinstance(data, list):
        return data

    return list(dict.fromkeys(data))


def get_random_str(str_len):
    """
    获取随机字符串
    :param str_len: 需要获取的长度
    :return:
    """
    str_list = ""
    for i in range(0, str_len):
        str_list = str_list + STR[int(random.uniform(0, len(STR)))]
    return str_list


def get_random_int(str_len):
    """
    获取随机字符串
    :param str_len: 需要获取的长度
    :return:
    """
    str_list = ""
    for i in range(0, str_len):
        str_list = str_list + INTS[int(random.uniform(0, len(INTS)))]
    return str_list


def generate_body_sort_script(sort='desc', **params):
    """生成es权重排序的body数据"""
    inline = []
    for key in params:
        inline.append("doc['{}'].value * params.{}".format(key, key))

    inline = "+".join(inline)

    body = {
        "sort": {
            "_script": {
                "type": "number",
                "script": {
                    "lang": "painless",
                    "inline": inline,
                    "params": params
                },
                "order": sort
            }
        }
    }
    return body


def generate_body(sort='desc', _script=None, match=None, term=None,
                  _range=None):
    '''构造esbody'''
    body = {}
    if _script:
        body = generate_body_sort_script(sort=sort, **_script)

    body['query'] = {
        "bool": {
            "must": [],
            "filter": []
        }
    }
    if match:
        for key, value in match.iteritems():
            body['query']['bool']['must'].append(
                {"match":
                    {
                        key: {
                            "query": value,
                            "operator": "and"
                        }
                    }
                }
            )

    if term:
        for key, value in term.iteritems():
            body['query']['bool']['filter'].append({"term": {key: value}})

    if _range:
        for key, value in _range.iteritems():
            body['query']['bool']['filter'].append({"range": {key: value}})

    return body


def check_back_card(card_num):
    """检查银行卡的合法性"""
    total = 0
    even = True

    if isinstance(card_num, int):
        card_num = str(card_num)

    check_num = card_num[-1]
    for item in card_num[-2::-1]:
        item = int(item)
        if even:
            item <<= 1

        if item > 9:
            item -= 9

        total += item
        even = not even

    return int(check_num) is (10 - (total % 10)) % 10


def hide_card(card):
    """隐藏卡号"""
    if isinstance(card, int):
        card = str(card)

    length = len(card)
    prefix_length = 3
    suffix_length = 4
    hide_length = length - prefix_length - suffix_length

    return '{}{}{}'.format(card[:prefix_length], '*' * hide_length,
                           card[length - suffix_length:])


def get_thumbnail_url(artwork_url, weight=None, height=None, q_auto=False):
    """获取cloudinary服务器的缩略图"""
    if not artwork_url:
        return artwork_url
    artwork_url = artwork_url.replace('https://res.cloudinary.com',
                                      'http://res.lightcircle.vegocdn.net')

    find_index = artwork_url.find('image/upload')

    if find_index == -1:
        return artwork_url

    if q_auto:
        artwork_url = artwork_url.replace('image/upload', 'image/upload/q_auto')

    if not weight or not height:
        return artwork_url

    isexist_weight = artwork_url.find('w_')
    isexist_height = artwork_url.find('H_')
    if isexist_height > find_index or isexist_weight > find_index:
        return artwork_url

    if q_auto:
        return artwork_url.replace(
            'image/upload/q_auto', 'image/upload/w_{}/h_{}/q_auto'.format(
                weight, height
            ))
    else:
        return artwork_url.replace(
            'image/upload', 'image/upload/w_{}/h_{}/q_auto'.format(
                weight, height
            ))


def is_emtry_str(content):
    """判断是否为空字符串"""
    if not content:
        return False
    if not isinstance(content, str):
        return False

    content = content.strip()

    if not content:
        return True
    else:
        return False


def generate_topic_name(key, id):
    """
    生成topic名称
    :param key: topic关键字
    :param id: 唯一标示
    :return:
    """

    return '{}_{}_{}'.format(key, app.config.get('ENV'), id)


def create_qrcode(content, stream=None, format=None):
    """
    生成二维码
    :param content: 二维码内容
    :param stream: 需要保存的方式，可以为文件地址或输入流
    :param format: 文件类型
    :param kwargs:
    :return:
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image()
    if stream:
        img.save(stream, format=format)
    return img


def add_seconds_to_time(t: datetime.time, seconds):
    s = t.hour * 3600 + t.minute * 60 + t.second + seconds
    hour = s // 3600
    minute = (s - hour * 3600) // 60
    second = s - hour * 3600 - minute * 60
    return datetime.time(hour, minute, second)


def cal_time_diff(t1: datetime.time, t2: datetime.time):
    t1 = datetime.datetime.combine(datetime.date(2001, 1, 1), t1)
    t2 = datetime.datetime.combine(datetime.date(2001, 1, 1), t2)
    return abs(t1 - t2)


def joint_name(first_name, last_name):
    """拼接名字"""
    res = RE_CHINESE.findall(first_name)
    if res:
        return '{}{}'.format(last_name, first_name)
    else:
        return '{} {}'.format(first_name, last_name)


def get_weather(lat, lng, key='d122fe39de94bf2c6c2ea443e9fef496'):
    """
    获取天气预报
    DOC:https://darksky.net/dev/docs/forecast
    """
    #  key1 = 'd122fe39de94bf2c6c2ea443e9fef496'
    #  key2 = 'ca5680b002774a7cba5cad57df33c20e'
    #  keys = ['04a0ab1e89d625503ad4d53c31622b04',
            #  'd122fe39de94bf2c6c2ea443e9fef496',
            #  'ca5680b002774a7cba5cad57df33c20e']

    def _f2c(f):
        """华氏度转变成摄氏度"""
        return float('{:0.2f}'.format((float(f) - 32) / 1.8))

    def _format_hour(h):
        """格式化小时内天气"""
        h['temperature'] = _f2c(h['temperature'])
        h['apparentTemperature'] = _f2c(h['apparentTemperature'])
        h['dewPoint'] = _f2c(h['dewPoint'])
        return h

    def _format_day(d):
        """格式化每天天气"""
        d['temperatureMin'] = _f2c(d['temperatureMin'])
        d['temperatureMax'] = _f2c(d['temperatureMax'])
        d['apparentTemperatureMin'] = _f2c(d['apparentTemperatureMin'])
        d['apparentTemperatureMax'] = _f2c(d['apparentTemperatureMax'])
        d['dewPoint'] = _f2c(d['dewPoint'])
        return d

    def _format(d):
        """格式化天气"""
        d['scale'] = '°F'

        if d.get('timezone') and 'America' not in d.get('timezone'):
            d['currently'] = _format_hour(d['currently'])
            d['hourly']['data'] = [_format_hour(o) for o in d['hourly']['data']]
            d['daily']['data'] = [_format_day(o) for o in d['daily']['data']]
            d['scale'] = '°C'

        return d

    try:
        url = 'https://api.darksky.net/forecast/{}/{},{}'
        res = requests.get(url.format(key, lat, lng))
        if res.status_code != 200:
            logger.error('weather error %s', res.content)
            #  res = requests.get(url.format(key2, lat, lng))
            #  if res.status_code != 200:
                #  logger.error('weather error %s', res.content)
        return _format(res.json())
    except Exception:
        logger.error(traceback.format_exc())
        return {}


class MysqlDB():
    def __init__(self, *args, **kwargs):
        """

        :param args:
            [0] database_uri
        :param kwargs:
            database_uri:数据库连接地址
        """
        database_uri = args[0] if args else kwargs.get('database_uri')
        self.config = urlparse(database_uri)

    def connect(self):
        """返回连接"""
        return pymysql.connect(
            host=self.config.hostname,
            port=self.config.port,
            user=self.config.username,
            password=self.config.password,
            db=self.config.path[1:],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def query(self, sql, params):
        """
        查询操作
        :param sql:
        :param params:
        :return:
        """
        conn = self.connect()
        try:
            cursor = conn.cursor()

            cursor.execute(sql, params)
            conn.commit()
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception:
            app.logger.error(traceback.format_exc())
            return []
        finally:
            conn.close()

    def execute(self, sql, params):
        """
        更新操作
        :param sql:
        :param params:
        :return:
        """
        conn = self.connect()
        try:
            cursor = conn.cursor()

            result = cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            return result
        except Exception:
            app.logger.error(traceback.format_exc())
            return False
        finally:
            conn.close()


def get_network_image_wh(url):
    """获取网络图片的宽高"""
    try:
        i = Image.open(io.BytesIO(requests.get(url).content))

    except Exception:
        app.logger.error(traceback.format_exc())
        return (0, 0)
    return i.size

def get_value(url, k):
    """获取地址中参数值"""
    nk = '{}='.format(k)
    if nk not in url:
        return None

    b = url.find(nk) + len(nk)  # 获取开始位置
    e = url.find('&', b) if url.find('&', b) != -1 else len(url)    # 结束位置
    v = url[b:e]
    return v

def generate_dict(keys, values):
    """生成字典"""
    def _fmt_i(k, v):
        return k ,v

    def _fmt(o):
        r = list(map(_fmt_i, keys, o))
        return {k: v for k, v in r}
    return _fmt(values)

def get_hour_time_from_timestamp(ts):
    """通过时间戳生成当前的小时时间"""
    d = datetime.datetime.fromtimestamp(ts)
    return datetime.datetime(d.year, d.month, d.day, d.hour, 0, 0)

def sort_dict(d, keys, sort_key, reverse=False):
    """对不规则的字典进行排序"""
    lines = [{keys[0]: k, keys[1]: v} for k, v in d.items()]
    lines.sort(key=lambda x: x[sort_key], reverse=reverse)
    return lines

def get_ip_detail(ip):
    """获取 ip 地址的详细信息"""
    # TODO 处理ip
    return False, data
    url = 'http://ip-api.com/json/{}'.format(ip)
    res = requests.get(url)
    data = res.json()
    status = data.get('status')
    if status == 'success':
        return True, data
    return False, data

def fen_to_yuan(amount):
    return round(float(amount) / 100, 2)

def math_div(a, b, digits=2):
    fmt = '{{:.{}f}}'.format(digits)
    res = fmt.format(a / b)
    return float(res)

def sequence(obj):
    """序列化"""
    if not obj:
        return obj
    res = msgpack.packb(obj, use_bin_type=True)
    return res

def unsequence(msg):
    """反序列"""
    if not msg:
        return msg
    res = msgpack.unpackb(msg, encoding='utf-8')
    return res

def get_bj_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=8)

def get_zone_time(time_zone):
    return datetime.datetime.utcnow() + datetime.timedelta(hours=time_zone)

def get_zone_date(time_zone):
    date_time = datetime.datetime.utcnow() + datetime.timedelta(hours=time_zone)
    return date_time.date()

def fmt_image(url, aliyun_q = 70):
    '''格式化图片'''
    if 'mewephoto.oss-cn-beijing.aliyuncs.com' in url:
        #  return '{}?x-oss-process=image/auto-orient,1/quality,q_{}'.format(url,
            #  aliyun_q)
        return '{}?x-oss-process=image/resize,w_1920/auto-orient,1'.format(url)

    return url

def get_args_by_request(request):
    '''根据 request 获取参数'''
    content_type = request.content_type or ''
    _args = {}
    if 'application/x-www-form-urlencoded' in content_type:
        _args = request.form
    elif 'application/json' in content_type:
        _args = request.json
    else:
        _args = request.args
    return _args

def fmt_cdn_url(url):
    '''地址替换为 cdn 地址'''
    new_url = url
    if 'mewevideopublic.oss-cn-beijing.aliyuncs.com' in url:
        new_url = url.replace('mewevideopublic.oss-cn-beijing.aliyuncs.com', 'videopublic.vego.tv')
    elif 'mewevideo.oss-cn-beijing.aliyuncs.com' in url:
        new_url = url.replace('mewevideo.oss-cn-beijing.aliyuncs.com', 'video.vego.tv')

    return new_url

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def get_video_duration(path):
    '''获取视频的时长'''

    duration = 0
    try:
        BaseConfig.NODE_AWS_HEAD
        head = BaseConfig.NODE_AWS_HEAD
        if 'aliyuncs.com' in path:
            head = BaseConfig.NODE_ALI_HEAD
        res = requests.post('{}/video_detail'.format(head), json=dict(url=path))
        logger.debug(res)
        data = res.json()
        logger.debug(path)
        logger.debug(data)

        dur = data.get("data").get("duration")
        if dur:
            duration = int(dur)
    except Exception as e:
        logger.error(e)
    return duration

def get_location_by_ip(ip):
    '''根据ip获取地址信息 https://ipstack.com/'''
    url = "http://api.ipstack.com/{}?access_key=a5c44ddd9262ad9b882171f79e1607f5".format(ip)
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    if not data.get("latitude") or not data.get("longitude"):
        return None

    if not data.get("region_code"):
        status, detail = get_ip_detail(ip)
        if status:
            data['region_code'] = detail['region']
            data['region_name'] = detail['regionName']
            data['city'] = detail['city']
            data['zip'] = detail['zip']
    return data


def get_month_days(date):
    '''一个月的天数'''
    s = date.split('-')
    year = int(s[0])
    month = int(s[1])
    days = 30
    if month in (1, 3, 5, 7, 8, 10, 12):
        days = 31
    elif month in (4, 6, 9, 11):
        days = 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            days = 29
        else:
            days = 28

    return days

def translation(text, dest='en'):
    '''翻译'''
    translate = Translator()
    result = translate.translate(text, dest=dest)
    return result.text


def getBetweenDay(begin_date, end_date):
    '''获取一段时间内的时间列表'''
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

def gold2fen(gold):
    '''金币转人民币（分）'''
    return gold * 42

def gold2dollar(gold):
    '''金币转美元'''
    return int(gold * 0.00612 * 100) / 100

def fen2gold(fen):
    '''人民币（分）转金币'''
    return int(fen / 42 * 100)

def dollar2fen(dollar):
    '''美元转人民币（分）'''
    return int(float(dollar) * 6699)

def is_want_update():
    return True if datetime.datetime.now().minute % 2 else False

def tencent_send_template_msg(mobile_code, mobile, params, tpl_id=377214):
    '''发送腾讯云的模板消息'''

    rand = get_random_str(10)
    t = int(time.time())
    sig = sha256('appkey={}&random={}&time={}&mobile={}'.format(
        '97def9a890aff93a928016428ab9ee20', rand, t, mobile
    ))
    url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms?sdkappid={}&random={}'.format(
        '1400234753', rand
    )
    data = {
        "params": params,
        "sig": sig,
        "sign": "东方嘉禾",
        "tel": {
            "mobile": mobile,
            "nationcode": mobile_code.replace('+', '')
        },
        "time": t,
        "tpl_id": tpl_id
    }
    logger.debug('tencent data %s', data)
    res = requests.post(url, json=data)
    logger.debug('tencent msg %s', res.json())
    return res.json()

def hans2py(hans):
    '''汉字转拼音'''
    hans = hans.lower()
    hans = hans.split()
    all_words = lazy_pinyin(hans,
        errors=lambda x: x if find_english(x) else None)
    first_letters = [o[0] for o in all_words]
    res = dict(all_words = all_words, first_letters = first_letters)
    return res

def get_name_field_by_language(language, prefix='name'):
    '''根据语言获取字段名'''
    if language == 'zh':
        return prefix
    else:
        return '{}_{}'.format(prefix, language)

