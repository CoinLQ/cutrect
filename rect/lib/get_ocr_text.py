#! python 3.5
# -*- coding:utf8 -*-
# Program:
#   for testing the API of dzjOCR
#   post the data to the server and show the returned data
# History:
#   2017.12.17  XianHu
# **********************Founction document***********************
# Founction 1:post the data to server
# Founction 2:show datas
# ***************************************************************
import urllib.request
import urllib.parse
import json


USER_ID = "SCUTDLVC"
TABLE_NAME = "OCR_DB"
APIURL = 'http://54.223.50.62/demo/ocr/'

def testAPI(imgBase64):
    UserID = USER_ID

    post_data = {'Image': imgBase64, 'UserID': UserID}
    URL = APIURL
    ret = urllib.request.urlopen(url=URL, data=urllib.parse.urlencode(post_data).encode('utf-8')).read()
    ret = str(ret, encoding='utf-8')
    ret_dict = json.loads(ret)

    return ret_dict

#****************************method*****************************


def jsonToNewJson(jsonData):
    vectorList = list()
    if jsonData['code'] == 0:
        bboxList = jsonData['data']['bboxList']
        groupDataList = list()

        # 获取位置坐标
        if len(bboxList) % 4 == 0:
            for x in range(int(len(bboxList) / 4)):
                groupDataList.append(bboxList[4 * x:4 * x + 4])
            for x in range(len(groupDataList)):
                vectorDic = {'x1': groupDataList[x][0], 'y1': groupDataList[x][1], 'x2': groupDataList[x][2],
                             'y2': groupDataList[x][3]}
                vectorList.append(vectorDic)
        else:
            print('数据不是4的整数倍。')
        # 获取置信度数据, 获取文字数据
        confList = jsonData['data']['confList']
        labelList = jsonData['data']['labelList']
        if len(confList) > 0:
            for x in range(int(len(confList))):
                vectorDic = vectorList[x]
                vectorDic['cc'] = confList[x]
                vectorDic['word'] = labelList[x]

    else:
        print('数据报错：', jsonData['message'])
    return vectorList

