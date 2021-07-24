#!/usr/bin/env python
# -*-coding:utf-8-*-
# by 'hollowman6' from Lanzhou University(兰州大学)

import os
import json
import requests
import urllib.parse

sckey = os.environ['SERVERCHANSCKEY']
pptoken = os.environ['PPTOKEN']
pptopic = os.environ['PPTOPIC']
title = os.environ['TITLE']
message = os.environ['MSG']
content = os.environ['CONTENT']
image = os.environ['IMAGE']
corpid = os.environ['CORPID']
corpsecret = os.environ['CORPSECRET']
agentid = os.environ['AGENTID']
access_token = ""
errorNotify = ""

if not title:
    raise Exception("未设置 `TITLE[name]` Actions Secret!")

def exwechat_get_access_token():
    url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    params = {
        'corpid': corpid,
        'corpsecret': corpsecret
    }
    req = urllib.request.Request(url, data=str(json.dumps(params)).encode('utf-8'))
    resp = urllib.request.urlopen(req)
    resp_json = json.loads(resp.read())
    if 'access_token' in resp_json.keys():
        return resp_json['access_token']
    else:
        raise Exception('请检查CORPID和CORPSECRET是否正确！\n' + resp.text)

def exwechat_get_ShortTimeMedia(img_url):
    media_url = f'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=file'
    f = open(img_url, "rb").read()
    req = urllib.request.Request(media_url, data=str(json.dumps({'file': f})).encode('utf-8'))
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())['media_id']


def exwechat_send(title, digest, content):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    data = {
        "touser": "@all",
        "agentid": agentid,
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    if content and image:
        data["msgtype"] = 'mpnews'
        data["mpnews"] = {
            "articles": [
                {
                    "title": title,
                    "thumb_media_id": exwechat_get_ShortTimeMedia(image),
                    "author": "Hollow Man",
                    "content_source_url": "https://github.com/HollowMan6/Wechat-Timed-Message/actions",
                    "content": content,
                    "digest": digest
                }
            ]
        }
    else:
        data["msgtype"] = "textcard"
        data["textcard"] = {
            "title": title,
            "description": digest,
            "url": "https://github.com/HollowMan6/Wechat-Timed-Message/actions"}
    req = urllib.request.Request(url, data=str(json.dumps(data)).encode('utf-8'))
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

if sckey:
    try:
        host = "https://sctapi.ftqq.com/"
        title = urllib.parse.quote_plus(title.replace('\n', '\n\n'))
        message = urllib.parse.quote_plus(message.replace('\n', '\n\n'))
        res = urllib.request.urlopen(host + sckey + ".send?text=" + title +
                            "&desp=" + message)
        response = res.read().decode('utf-8')
        result = json.loads(response)
        if result['data']['errno'] == 0:
            print("Server酱推送成功!")
        else:
            errorNotify += "Server酱推送错误: " + response + "\n"
    except Exception as e:
        print(e)
        errorNotify += "Server酱推送错误!\n"
else:
    print("未设置SERVERCHANSCKEY，尝试使用PushPlus...")

if pptoken:
    try:
        host = "http://pushplus.hxtrip.com/"
        user = ""
        if not message:
            message = title
            title = ""
        title = urllib.parse.quote_plus(title.replace('\n', '<br>'))
        message = urllib.parse.quote_plus(message.replace('\n', '<br>'))
        res = urllib.request.urlopen(host + "send?token=" + pptoken + "&title=" + title +
                            "&content=" + message + "&template=html&topic=" + pptopic)
        response = res.read().decode('utf-8')
        result = json.loads(response)
        if result['code'] == 200:
            print("成功通过PushPlus将结果通知给相关用户!")
        else:
            errorNotify += "PushPlus推送错误: " + response + "\n"
    except Exception as e:
        print(e)
        errorNotify += "PushPlus推送错误!\n"
else:
    print("未设置PPTOKEN！")

if corpid:
    info = ""
    if corpsecret:
        if agentid:
            try:
                access_token = exwechat_get_access_token()
                res = exwechat_send(title, message, content)
                result = res
                if result['errcode'] == 0:
                    print("成功通过企业微信将结果通知给用户!")
                else:
                    errorNotify += "企业微信推送错误: " + res.text + "\n"
            except Exception as e:
                print(e)
                errorNotify += "企业微信推送错误!\n"
        else:
            print("未设置AGENTID，无法推送到企业微信！")
    else:
        print("未设置CORPSECRET，无法推送到企业微信！")
else:
    print("未设置CORPID！")

if errorNotify:
    raise Exception(errorNotify)
