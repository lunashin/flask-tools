#!/usr/bin/python3

import csv
import datetime
import sys
import os




# 除外する日(祝日など) 2022年版
holiday_list = [
'2022/01/01', 
'2022/01/03', 
'2022/01/10', 
'2022/02/11', 
'2022/02/23', 
'2022/03/21', 
'2022/04/29', 
'2022/05/03', 
'2022/05/04', 
'2022/05/05', 
'2022/07/18', 
'2022/08/11', 
'2022/09/19', 
'2022/09/23', 
'2022/10/10', 
'2022/11/03', 
'2022/11/23', 
'2022/12/29', 
'2022/12/30',
'2023/01/02',
'2023/01/03',
'2023/01/09',
]



###############################################
# Class
###############################################

# レコード管理
class schedule_manager:
    list = []
    role_list = []
    index_name = -1
    index_days = -1
    index_role = -1
    startDateStr = ""

    def __init__(self):
        self.list = []
        self.role_list = []
        self.index_name = -1
        self.index_days = -1
        self.index_role = -1
        self.startDateStr = ""

    # CSVフィールドインデックス設定 (0 〜)
    def setIndexName(self, index):
        self.index_name = index
    def setIndexDays(self, index):
        self.index_days = index
    def setIndexRole(self, index):
        self.index_role = index
    def setStartDate(self, startDateStr):
        self.startDateStr= startDateStr

    # ストリームからCSV読み取り
    def read_csv_from_stream(self, st, delimiter):
        reader = csv.reader(st, delimiter=delimiter)
        index = 0
        for row in reader:
            # 先頭行はスキップ
            if index == 0:
                index = index + 1
                continue
            
            role = ""
            if self.index_role != -1:
                role = row[self.index_role]
            
            # レコード追加
            self.add(row[self.index_name], int(row[self.index_days]), role)
            index = index + 1
    
    # CSVファイルから読み取り
    def read_csv_from_file(self, filename, delimiter):
        with open(filename) as f:
            self.read_csv_from_stream(f, delimiter)

    # レコード追加
    def add(self, name, days, role):
        print("add: ", name, days, role)
        rec = schedule_record()
        rec.set(name, days, role)
        self.list.append(rec)

        if role not in self.role_list:
            self.role_list.append(role)

    # 開始日時と終了日時を決定
    def detect_start_end(self, start_date):
        # role毎に処理する
        for role in self.role_list:
            base_date = start_date
            for item in self.list:
                if item.role == role:
                    # 開始日決定 (休日なら進める)
                    while self.isHoliday(base_date) == True:
                        base_date = base_date + datetime.timedelta(days=1)

                    # 開始日
                    item.start_date = base_date
                    # 終了日(週末を考慮)
                    days_new = self.calc_days(base_date, item.days)
                    item.end_date = base_date + datetime.timedelta(days=days_new - 1)
                    # 次のタスクの開始日
                    base_date = item.end_date + datetime.timedelta(days=1)

    # 週末 or 祝日かどうか
    def isHoliday(self, target_date):
        # 週末
        if target_date.weekday() == 5 or target_date.weekday() == 6:
            return True
        # 祝日
        for holiday in holiday_list:
            date_dt = datetime.datetime.strptime(holiday, '%Y/%m/%d')
            if target_date == date_dt:
                # print("holiday hit: ", str(target_date) , str(date_dt))
                return True
        return False

    # 週末を考慮した日数を算出
    def calc_days(self, base_date, days):
        base_days = days
        cnt = 0
        while cnt < base_days:
            target_date = base_date + datetime.timedelta(days=cnt)
            # print(target_date)
            # if target_date.weekday() == 5 or target_date.weekday() == 6:
            #     base_days = base_days + 1
            if self.isHoliday(target_date):
                base_days = base_days + 1
            cnt = cnt + 1
        # print (str(base_days))
        return base_days

    def show(self):
        for item in self.list:
            print(item.name + "/" + str(item.days) + "/" + item.start_date.strftime('%Y-%m-%d') + "/" + item.end_date.strftime('%Y-%m-%d'))

    # CSVへ出力
    def write_csv(self, outfile, delimiter):
        # write csv
        with open(outfile, mode='w') as f:
            # ヘッダ
            f.write("No" + delimiter + "Name"  + delimiter + "days" + delimiter + "role" + delimiter + "date" + "\n")
            # 本体
            number = 1
            for item in self.list:
                f.write(str(number))
                f.write(delimiter)
                f.write(item.name)
                f.write(delimiter)
                f.write(str(item.days))
                f.write(delimiter)
                f.write(item.role)
                f.write(delimiter)
                f.write(item.start_date.strftime('%Y/%m/%d') + " → " + item.end_date.strftime('%Y/%m/%d'))
                f.write(delimiter)
                f.write("\n")
                number = number + 1




# レコード
class schedule_record:
    name = ""
    days = 0
    start_date = None
    end_date = None
    role = ""

    def __init__(self):
        self.name = ""
        self.days = 0
        self.start_date = None
        self.end_date = None
        self.role = 0

    def set(self, name, days, role):
        self.name = name
        self.days = days
        self.role = role

