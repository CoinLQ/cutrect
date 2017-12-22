

import re

linePattern = re.compile(r'(?P<pageImg>\w+\.jpg) (?P<rectData>.+)\!(?P<txtData>.+)')
separate = re.compile(';')
rectPattern = re.compile(r'(?P<x>\d+),(?P<y>\d+),(?P<w>\d+),(?P<h>\d+),(?P<cc>[0-9]+\.[0-9]+)')
wordPattern = re.compile(r'(?P<word>[\x80-\xff]+)')

def parsePage(line):
    lineMatcher = linePattern.match(line)
    if lineMatcher:
        img = lineMatcher.group('pageImg')
        rectData = lineMatcher.group('rectData')
        txtData = lineMatcher.group('txtData')

        rectColumnArr = separate.split(rectData)
        txtColumnArr = separate.split(txtData)
        #maxColumnCount = max(len(rectColumnArr), len(txtColumnArr))
        columnNum = 0
        pageRectJson = []
        for i in range(len(rectColumnArr)): #以切块数据列数为准.
            rectIter = rectPattern.finditer(rectColumnArr[columnNum])
            txtColumn = txtColumnArr[columnNum]
            columnNum += 1 #按人类习惯列号以1为开始
            lineNum = 0
            columnJson = []
            if rectIter:
                for rect in rectIter:
                    rectJson = rect.groupdict()
                    word = txtColumn[lineNum]
                    if word: rectJson['word'] = word
                    lineNum += 1 #按人类习惯用法行号以1为开始.
                    rectJson['ln'] = lineNum
                    rectJson['cn'] = columnNum
                    columnJson.append(rectJson)
                    #todo 保存rectJson到数据库中.
            pageRectJson.append({columnNum: columnJson})
        #todo 保存PageRectJson到数据库表PageRect中.





#
# 3.2.2 Match对象的方法
# group([index|id]) 获取匹配的组，缺省返回组0,也就是全部值
# groups()               返回全部的组
# groupdict()           返回以组名为key，匹配的内容为values的字典


if __name__ == "__main__":
    line = "0001_001_26_01.jpg 120,321,188,398,0.980491,122,402,196,479,0.998218;214,324,295,397,0.998101,208,398,293,477,0.99899!麗象;遷儀"
    parseLine(line)
