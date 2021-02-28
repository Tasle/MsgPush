# -*- coding: utf8 -*-

import requests
import json
import logging
import os
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class pusher:
    def __init__(self, type, usr, tile, msg, url):
        self.base_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?'
        self.req_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token='
        # self.corpid = ''  # 企业ID
        # self.corpsecret = ''  # 应用Secret
        # self.agentid =   # 应用ID
        # 从scf环境变量获取数据
        self.corpid = os.environ['corpid']  # 企业ID
        self.corpsecret = os.environ['corpsecret'] # 应用Secret
        self.agentid = os.environ['agentid']  # 应用ID
        self.usr = usr
        self.msg = msg
        self.tile = tile
        self.url = url
        self.type = type

    def get_access_token(self):
        urls = self.base_url + 'corpid=' + self.corpid + '&corpsecret=' + self.corpsecret
        resp = requests.get(urls).json()
        access_token = resp['access_token']
        return access_token

    def send_message(self):
        data = self.get_message()
        req_urls = self.req_url + self.get_access_token()
        res = requests.post(url=req_urls, data=data)
        return res

    def get_message(self):
        if self.type == "tc":
            data = {
                "touser": self.usr,
                "toparty": "@all",
                "totag": "@all",
                "msgtype": "textcard",
                "agentid": self.agentid,
                "textcard": {
                    "title": self.tile,
                    "description": self.msg,
                    "url": self.url,
                    # "btntxt": "更多"
                },
                "safe": 0,
                "enable_id_trans": 0,
                "enable_duplicate_check": 0,
                "duplicate_check_interval": 1800
            }
        elif self.type == "tx":
            data = {
                    "touser": self.usr,
                    "toparty": "@all",
                    "totag": "@all",
                    "msgtype": "text",
                    "agentid": self.agentid,
                    "text": {
                        "content": self.msg
                    },
                    "safe": 0,
                    "enable_id_trans": 0,
                    "enable_duplicate_check": 0,
                    "duplicate_check_interval": 1800
                }
        data = json.dumps(data)
        return data


def main_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))
    logger.info("Received context: " + str(context))
    # 解析请求参数
    queryString = event['queryString']
    msg_type = queryString.get('type', 'tx')  # tx:文本 tc：卡片
    msg_title = queryString.get('text', None)
    msg_desp = queryString.get('desp', 'test')
    msg_usr = queryString.get('usr', '@all')
    msg_url = queryString.get('url', 'URL')
    test = pusher(type=msg_type, usr=msg_usr, tile=msg_title, msg=msg_desp, url=msg_url)  # usr参数为推送用户名，msg为消息文本
    resp = test.send_message()
    # 云函数固定返回值
    return {
        "isBase64Encoded": False,
        "statusCode": resp.status_code,
        "headers": {'Content-Type': 'application/json'},
        "body": json.dumps(resp.json())
    }