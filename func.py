import numpy as np
import pandas as pd
import copy
from oop import *


def timetables_from_excel(path, skiprows=1):
    timetable = pd.read_excel(open(path, 'rb'), skiprows=skiprows)

    M_K_timetable = []
    E_K_timetable = []

    for index, row in timetable.iterrows():
        if str(row['ID']).startswith('M_K'):
            M_K_timetable.append({row['ID']:row.values[2:9]})
        elif str(row['ID']).startswith('E_K'):
            E_K_timetable.append({row['ID']:row.values[2:9]})
        elif str(row['ID']).startswith('VYB_OSN'):
            M_K_timetable.append({row['ID']:row.values[2:9]})


    # M_K_timetable_np = np.array(M_K_timetable)
    # E_K_timetable_np = np.array(E_K_timetable)
    # M_K_timetable_np[M_K_timetable_np == 'о'] = 0
    # E_K_timetable_np[E_K_timetable_np == 'о'] = 0

    # clear_M_K = M_K_timetable_np[0:, 2:9]
    # clear_M_K = np.where(np.isnan(clear_M_K.astype(float)), 0, clear_M_K.astype(float))
    # clear_E_K = np.nan_to_num(E_K_timetable_np[0:, 2:9])
    # clear_E_K = np.where(np.isnan(clear_E_K.astype(float)), 0, clear_E_K.astype(float))
    #
    timetables = {
        "M_K": M_K_timetable,
        "E_K": E_K_timetable,
    }
    return timetables



def tasks_from_excel(path, skiprows=1):
    tasks = pd.read_excel(open(path, 'rb'), skiprows=skiprows)
    # print(tasks)

    days = tasks.drop_duplicates('Срок начала')['Срок начала'].tolist()

    isodays = []

    for day in days:
        isodays.append(str(day.isoformat()))

    m_tasks_in_day = {key: {'high': [], 'low': []} for key in isodays}
    e_tasks_in_day = copy.deepcopy(m_tasks_in_day)

    m_tasks = tasks[tasks['Отдел'] == 'VYB_MEC']
    e_tasks = tasks[tasks['Отдел'] == 'VYB_ELE']

    for day in days:
        m_tasks_in_day[str(day.isoformat())]['high'] = m_tasks[
            (m_tasks['Приоритет'] == 1) & (m_tasks['Срок начала'] == day)]
        m_tasks_in_day[str(day.isoformat())]['low'] = m_tasks[
            (m_tasks['Приоритет'] == 0) & (m_tasks['Срок начала'] == day)]

        e_tasks_in_day[str(day.isoformat())]['high'] = e_tasks[
            (e_tasks['Приоритет'] == 1) & (e_tasks['Срок начала'] == day)]
        e_tasks_in_day[str(day.isoformat())]['low'] = e_tasks[
            (e_tasks['Приоритет'] == 0) & (e_tasks['Срок начала'] == day)]

    tasks = {
        "m_tasks": m_tasks_in_day,
        "e_tasks": e_tasks_in_day
    }
    return tasks

def create_workers_from_array(timetables):

    M_K = timetables['M_K']
    E_K = timetables['E_K']

    m_workers =[]
    e_workers = []

    for worker in M_K:
        code, line = list(worker.keys())[0], list(worker.values())[0]
        line[line == 'о'] = 0
        clear_line = np.where(np.isnan(line.astype(float)), 0, line.astype(float)).tolist()
        m_workers.append(Worker(clear_line, code))

    for worker in E_K:
        code, line = list(worker.keys())[0], list(worker.values())[0]
        line[line == 'о'] = 0
        clear_line = np.where(np.isnan(line.astype(float)), 0, line.astype(float)).tolist()
        e_workers.append(Worker(clear_line, code))

    return m_workers, e_workers

def get_specials(specials):
    try:
        list = specials.split(' ')
        return list
    except AttributeError:
        return None


def tasks_from_df(tasks, day):
    m = tasks['m_tasks'][day]
    e = tasks['e_tasks'][day]

    m_list_obj = []

    for index, row in m['high'].iterrows():
        specials = get_specials(row['Особые исполнители'])
        m_list_obj.append(Task(row['Общее время'], row['Требуется человек'], True, row['Номер заказа'], specials))
    for index, row in m['low'].iterrows():
        specials = get_specials(row['Особые исполнители'])
        m_list_obj.append(Task(row['Общее время'], row['Требуется человек'], False, row['Номер заказа'], specials))
    # make for e too!
    return m_list_obj

