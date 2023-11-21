import openpyxl
from openpyxl.styles import Alignment
from datetime import datetime, timedelta
import calendar
from io import BytesIO
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File
from typing import Annotated
from fastapi import  UploadFile

def excel_to_json(file_path):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]

    data = []
    divisions = set()

    for row in sheet.iter_rows(min_row=2, values_only=True):
        row_data = dict(zip(headers, row))
        data.append(row_data)
        divisions.add(row_data['Подразделение'])
    return data, divisions

def sortByDivision(data, divisions):
    dataGroup = {}
    for division in divisions:
        dataGroup[division]=[]
    for item in data:
        dataGroup[item['Подразделение']].append(item)
    return dataGroup

def MergedVacation(data):
    
    new_divisions = {}
    # fill divisions
    for division in data:
        new_divisions[division] = []

    for division in data:
        item_division = data[division]
        # fill employees current division
        for employee in item_division:
            # check matches
            continue_iter = True
            for employees_in_list in new_divisions[employee["Подразделение"]]:
                # pass
                if employees_in_list["ФИО"] == employee["ФИО"]:
                    pass
                    continue_iter = False
                    break
            if continue_iter == False:
                continue

            employee_data = {
                "ФИО": employee["ФИО"],
                "отпуска": [],
                "дни": None
            }
            common_vacation_days = 0
            for employee in item_division:
                if employee_data["ФИО"] == employee["ФИО"]:
                    vacation = {
                            # "Дата с":       datetime.strptime(employee["Дата с"], '%d.%m.%Y'),
                            "Дата с":       employee["Дата с"],
                            "Дата по":      employee["Дата по"],
                            "Кол-во дней":  employee["Кол-во дней"],
                            "ЕСВ":          employee["ЕСВ"],
                        }
                    common_vacation_days = common_vacation_days + int(employee["Кол-во дней"])
                    employee_data["отпуска"].append(vacation)
                else:
                    continue
            employee_data["дни"] = common_vacation_days
            new_divisions[employee["Подразделение"]].append(employee_data)
    return new_divisions

def days_in_year(year):
    data = []
    for month in range(1, 13):
        days = calendar.monthrange(year, month)[1]
        data.append({
            "name": calendar.month_name[month], 
            "days": days
            })
    return data

def weeks_in_months(year):
    months = days_in_year(year)
    week_step = 7
    for month in months:
        weeks = []
        for start_day in range(1, month["days"] + 1, week_step):
            end_day = min(start_day + week_step - 1, month["days"])
            if start_day != end_day:
                # weeks.append(f"{start_day}-{end_day}")
                weeks.append([start_day,end_day])
            else:
                weeks.append([start_day])
            # weeks.append
        month["weeks"] = weeks
    return months

def setWeekCells(data, months):
    # итерация по отделам
    for division in data:
        # FOR DEBUG
        # if division != "Отдел по эксплуатации сети передачи данных":
        #     continue
        employees = data[division]

        # итерация по сотрудникам
        for employee in employees:
            employee['vacations_with_weeks'] = []
            # итерация по отпускам сотрудника
            for vacation in employee["отпуска"]:
                new_vacation = {}
                start_day = {
                    "month_number": int(vacation["Дата с"].split('.')[1]) - 1,
                    "day": int(vacation["Дата с"].split('.')[0]) 
                } 
                end_day = {
                    "month_number": int(vacation["Дата по"].split('.')[1]) - 1,
                    "day": int(vacation["Дата по"].split('.')[0])
                } 

                if start_day["month_number"] == end_day["month_number"]:     
                    for index, week in enumerate(months[start_day["month_number"]]["weeks"]):
                        if len(week)==2:
                            if start_day["day"] >= week[0] and start_day["day"] <= week[1]:
                                start_vacation = {
                                    "day"  : start_day["day"],
                                    "week" :  index,
                                    "month": start_day["month_number"],
                                }
                                new_vacation['start'] = start_vacation
                            if end_day["day"] >= week[0] and end_day["day"] <= week[1]:
                                end_vacation = {
                                    "day"  : end_day["day"],
                                    "week" :  index,
                                    "month": end_day["month_number"],
                                }
                                new_vacation['end'] = end_vacation
                            pass
                        if len(week)==1:
                            if start_day["day"] == week[0]:
                                start_vacation = { 
                                    "day"  : start_day["day"],
                                    "week" :  index,
                                    "month": start_day["month_number"],
                                }
                                new_vacation['start'] = start_vacation
                            if end_day["day"] == week[0]:
                                end_vacation = {
                                    "day"  : end_day["day"],
                                    "week" :  index,
                                    "month": end_day["month_number"],
                                }
                                new_vacation['end'] = end_vacation
                # отпуск начинается и заканчивается в разные месяца
                if start_day["month_number"] != end_day["month_number"]:
                    # start
                    for index, week in enumerate(months[start_day["month_number"]]["weeks"]):
                        if len(week)==2:
                            if start_day["day"] >= week[0] and start_day["day"] <= week[1]:
                                start_vacation = {
                                    "day"  : start_day["day"],
                                    "week" :  index,
                                    "month": start_day["month_number"],
                                }
                                new_vacation['start'] = start_vacation
                        # в ячейке недели 1 день
                        if len(week)==1:
                            if start_day["day"] == week[0]:
                                start_vacation = { 
                                    "day"  : start_day["day"],
                                    "week" :  index,
                                    "month": start_day["month_number"],
                                }
                                new_vacation['start'] = start_vacation
                    # end
                    for index, week in enumerate(months[end_day["month_number"]]["weeks"]):
                        if len(week)==2:
                            if end_day["day"] >= week[0] and end_day["day"] <= week[1]:
                                end_vacation = {
                                    "day"  : end_day["day"],
                                    "week" :  index,
                                    "month": end_day["month_number"],
                                }
                                new_vacation['end'] = end_vacation
                                pass
                        if len(week)==1:
                            if end_day["day"] == week[0]:
                                end_vacation = {
                                    "day"  : end_day["day"],
                                    "week" :  index,
                                    "month": end_day["month_number"],
                                }
                                new_vacation['end'] = end_vacation
                # отпуска с месяцами
                employee['vacations_with_weeks'].append(new_vacation)
    return data

def sortVacation(data):
    for division in data:
        for employee in data[division]:
            employee['отпуска'] = sorted(employee['отпуска'], key=lambda x: datetime.strptime(x['Дата с'], '%d.%m.%Y'))
            pass
    return data

#############################




app = FastAPI()
# cors
origins = ["http://localhost", "http://localhost:5173"]  # Замените этот список на разрешенные домены
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data")
async def getdata():
    months = weeks_in_months(2024)
    data, divisions = excel_to_json('отпуска 2024.xlsx')
    divisions = sortByDivision(data, divisions)
    divisions = MergedVacation(divisions)
    divisions = setWeekCells(divisions, months)
    divisions = sortVacation(divisions)

    return {"divisions": divisions, "months": months}

@app.post("/file")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        file_contents = await file.read()
        file_bytes_io = BytesIO(file_contents)

        months = weeks_in_months(2024)
        data, divisions = excel_to_json(file_bytes_io)
        divisions = sortByDivision(data, divisions)
        divisions = MergedVacation(divisions)
        divisions = setWeekCells(divisions, months)
        divisions = sortVacation(divisions)

        pass
    except Exception as e:
        pass
    
    return {"divisions": divisions, "months": months}


