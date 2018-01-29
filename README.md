# cutrect

[![python](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-v1.11-orange.svg)](https://www.djangoproject.com/)
[![Build Status](https://travis-ci.org/CoinLQ/LQCharacter.svg?branch=master)](https://travis-ci.org/CoinLQ/LQCharacter)
[![codecov](https://codecov.io/gh/CoinLQ/AnyCollating/branch/master/graph/badge.svg)](https://codecov.io/gh/CoinLQ/AnyCollating)
[![license-BSD](https://img.shields.io/badge/license-BSD-green.svg)](LICENSE)


切字🍆

## 安装环境搭建
基本思路是通过virtualenvwrapper在本地创建一个独立的env环境，

### 安装 python3
略
### 安装 virtualenvwrapper及启用环境下的pip

```
cd /tmp
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```
```
pip install --ignore-installed six virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv character --python=python3
```
### 安装python依赖包
```
  workon character
  pip install -r requirements.txt

```
### 加载测试数据
下载测试数据 all_data_fixtures.json
链接:https://pan.baidu.com/s/1dGN0NQx  密码:tci2
测试数据admin。 用户admin 密码admin123
```
  python manage.py migrate
  python manage.py loaddata ./all_data_fixtures.json
```
### 应用环境设置(可能)
把下列环境变量加入你的rc文件中，
```
export AWS_ACCESS_KEY=<input>
export AWS_SECRET_KEY=<input>
```
###
### 启动应用
```
  python manage.py runserver
```
### 本地测试
```
cmd> python manage.py test
```
### Celery本地调试
```
celery -A cutrect worker --loglevel=info
celery -A cutrect beat -l debug
```