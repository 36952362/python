import sqlite3
import time
import sys
import os

def unix_time(dt):
   # 转换成时间数组
   timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
   # 转换成时间戳
   timestamp = int(time.mktime(timeArray))*1000
   return timestamp


def local_time(timeNum):
   timeStamp = float(timeNum / 1000)
   timeArray = time.localtime(timeStamp)
   otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
   return otherStyleTime

def exportMessagetodic(values):
   for i in range(0,len(values)):
      talker = values[i][2] 
      if talker not in allmessages:
         messageList = list()
         allmessages[talker] = messageList
      messageList = allmessages[talker]
      messageList.append(values[i])

def dumpAllMessages(allmessages):
   for key in allmessages:
      dumpEachMessages(key, allmessages[key])

def dumpEachMessages(talker, eachMessageList):
   formattedMessages = list()
   for eachMessage in eachMessageList:
      formatEachMessage(talker, eachMessage, formattedMessages)
   exportMessagetoFile(talker, formattedMessages)


def exportMessagetoFile(talker,formattedMessages):
   fileName = os.path.join(output_dir, talker + '的聊天记录.txt')
   with open(fileName,'wb') as f:
      for eachMessage in formattedMessages:
         f.write((eachMessage + '\n').encode('utf-8'))

def formatPersonalMessage(talker, eachMessage, formattedMessages):
   if needDump(eachMessage[4]):
      finalString = local_time(eachMessage[1])
      if eachMessage[0] == 0:
         finalString = finalString + ' ' + talker + ':'
      else:
         finalString = finalString + ' 我：'
      finalString = finalString + eachMessage[4]
      formattedMessages.append(finalString)

def formatGroupMessage(eachMessage, formattedMessages):
   if needDump(eachMessage[4]):
      finalString = local_time(eachMessage[1])
      if eachMessage[0] == 1:
         finalString = finalString + ' 我:'
      finalString = finalString + ' ' + eachMessage[4]
      formattedMessages.append(finalString)


def formatEachMessage(talker, eachMessage, formattedMessages):
   if isGroup(talker):
      formatGroupMessage(eachMessage, formattedMessages)
   else:
      formatPersonalMessage(talker, eachMessage, formattedMessages)

def isGroup(talker):
   if 'chatroom' in talker:
      return True
   return False

def needDump(eachMessage):
   if '<msg>' in eachMessage:
      return False
   if 'wxid_' in eachMessage:
      return False
   return True

db_file = sys.argv[1]
output_dir = sys.argv[2]
try:
    os.mkdir(output_dir)
except:
    pass
if not os.path.isdir(output_dir):
    sys.exit("创建目录{}失败".format(output_dir))
        
conn = sqlite3.connect(db_file)
c = conn.cursor()
b = unix_time("2020-02-24 01:01:01")  #开始时间
e = unix_time("2020-03-05 01:01:01")  #结束时间

#sql = "select isSend,createTime,talker,type,content from message where talker = 'wxid_' and createTime > "+str(b)+" and createTime < "+str(e)+" and type = '1'order by createTime"
sql = "select isSend,createTime,talker,type,content from message order by createTime"
cursor = c.execute(sql)
values = cursor.fetchall()
allmessages = dict()
exportMessagetodic(values)
conn.close()
dumpAllMessages(allmessages)