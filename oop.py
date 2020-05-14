import operator
import random
from shapely import geometry
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from shapely.ops import cascaded_union
from itertools import combinations
import numpy as np
import pandas as pd


class Timeline(object):
    """docstring"""

    def __init__(self, length, x, y):
        """Constructor"""
        self.length = length
        self.x = x
        self.y = y

    def relocate_x(self, limx):
        self.x = random.uniform(0, limx)  # check

    def rectangle(self, color):
        return Rectangle((self.x, self.y), self.length, 1, linewidth=1, edgecolor=color, facecolor='none', hatch='/')

    def rnd_relocate(self, limx, limy):
        self.x = random.uniform(0, limx-self.length)
        self.y = random.randint(0, limy-1)
        pass

    def relocate(self, x, y):
        self.x = x
        self.y = y
        pass


    def polygon(self):
        bottom_left = [self.x, self.y]
        bottom_right = [self.x + self.length, self.y]
        top_left = [self.x, self.y + 1]
        top_right = [self.x + self.length, self.y + 1]
        poly = geometry.Polygon([bottom_left, bottom_right, top_right, top_left])
        return poly


class Task(object):
    """docstring"""

    def __init__(self, duration, workers, priority, num, specials=None):
        """Constructor"""
        if specials is None:
            specials = []
        self.num = num
        self.priority = priority
        self.workers = workers
        self.duration = duration
        self.specials = specials

        timelines = []
        for i in range(workers):
            t = Timeline(duration, 0, 0)
            timelines.append(t)
        self.timelines = timelines

    def total(self):
        return self.workers * self.duration

    def rectangles(self, color):
        rectangles = []
        for timeline in self.timelines:
            rectangles.append(timeline.rectangle(color))
        return rectangles

    def rnd_relocate(self, field, limx, limy):
        x = random.uniform(0, limx-self.duration)
        y_list = []
        for special in self.specials:
            codeline = field.y_by_code(special)
            assert codeline!=-1
            y_list.append(codeline)
        while len(y_list) < self.workers:
            y_list.append(random.randint(0, limy-1))
            y_list = list(dict.fromkeys(y_list))

        for index, timeline in enumerate(self.timelines):
            timeline.relocate(x, y_list[index])

    def rnd_step(self, field, limx, limy):

        x_dir = random.randint(0, 1)
        x_val = random.uniform(0, 1)
        y_list = []
        for special in self.specials:
            codeline = field.y_by_code(special)
            assert codeline != -1
            y_list.append(codeline)

        for tm in self.timelines:
            if tm.y not in y_list:
                y_dir = random.randint(0, 1)
                if y_dir == 1:
                    tm.y = min(tm.y + 1, limy-1)
                else:
                    tm.y = max(tm.y - 1, 0)

            if x_dir == 1:
                tm.x = min(tm.x + x_val, limx-self.duration)
            else:
                tm.x = max(tm.x - x_val, 0)









class Worker(object):
    """docstring"""

    def __init__(self, schedule, code):
        """Constructor"""
        self.code = code
        self.schedule = schedule

    def avaliable(self, day):
        return True if self.schedule[day] > 0 else False


class Timetable(object):
    """docstring"""

    def __init__(self, day, workers):
        """Constructor"""
        self.day = day
        day_workers = {}
        for worker in workers:
            if worker.avaliable(day):
                day_workers[worker.code] = worker.schedule[day]

        self.day_workers = day_workers



class Field(object):

    def __init__(self, timetable, tasks, randomized = True):
        """Constructor"""
        self.timetable = timetable
        self.tupled = sorted(self.timetable.day_workers.items(), key=operator.itemgetter(1), reverse=True)
        self.len_y = round(len(timetable.day_workers))
        hours = list(timetable.day_workers.values())
        self.len_x = round(max(hours))

        if randomized:
            for task in tasks:
                task.rnd_relocate(self, self.len_x, self.len_y)

        self.tasks = tasks

    def randomize_timelines(self):
        for task in self.tasks:
            task.rnd_relocate(self, self.len_x, self.len_y)

    def total_area(self):
        return sum(list(self.timetable.day_workers.values()))

    def total_task_times(self):
        total = 0
        for task in self.tasks:
            total += task.total()
        return total

    def y_by_code(self, code):
        # tupled = sorted(self.timetable.day_workers.items(), key=operator.itemgetter(1), reverse=True)
        for num, worker in enumerate(self.tupled, start=0):
            if code == worker[0]:
                return num

        return -1

    def code_by_y(self, y):
        return  self.tupled[y][0]



    def statistics(self):
        print("Исходные данные:")
        print("Всего доступно часов:" + str(self.total_area()))
        print("Общее число часов заданий:" + str(self.total_task_times()))
        print("Анализ расписания:")
        print("Суммарное время недоработки:" + str(self.hours_left()))
        print("Суммарное число наложений:" + str(self.task_intersections()))
        print("Функция ошибки:" + str(self.loss()))

    def polygon(self, show_plot=False):
        # tupled = sorted(self.timetable.day_workers.items(), key=operator.itemgetter(1), reverse=True)
        # print(tupled)
        pointList = [[0, 0]]
        top_right = []
        for num, worker in enumerate(self.tupled, start=0):
            bottom_right = [worker[1], num]
            top_right = [worker[1], num + 1]
            pointList.append(bottom_right)
            pointList.append(top_right)
        top_left = [0, top_right[1]]
        pointList.append(top_left)
        poly = geometry.Polygon(pointList)
        if show_plot:
            x, y = poly.exterior.xy
            plt.plot(x, y)
            plt.show()
        return poly

    def hours_left(self):
        tt_poly = self.polygon()
        # print(tt_poly.area)
        # print(self.statistics())
        for task in self.tasks:
            for tl in task.timelines:
                tl_poly = tl.polygon()
                tt_poly = tt_poly.difference(tl_poly)

        # print(tt_poly.area)
        return tt_poly.area

    def task_intersections(self):
        tl_list = []
        for task in self.tasks:
            for tl in task.timelines:
                tl_list.append(tl.polygon())

        intersection = cascaded_union(
            [a.intersection(b) for a, b in combinations(tl_list, 2)]
        )
        return intersection.area

    def not_completed_task_times(self):
        tt_poly = self.polygon()
        not_completed_task_times = 0

        for task in self.tasks:
            error = 0
            for tl in task.timelines:
                # error += tl.polygon().difference(tt_poly).area
                error += tl.polygon().difference(tt_poly).area
            if error > 0:
                # not_completed_task_times += task.total()
                not_completed_task_times = error

        return not_completed_task_times

    def right_distance(self):
        total = 0
        for task in self.tasks:
            for tl in task.timelines:
                total += self.len_x-tl.length - tl.x
        return total

    def left_distance(self):
        total = 0
        for task in self.tasks:
            for tl in task.timelines:
                total += tl.x
        return total

    def loss(self):
        return self.task_intersections() + self.hours_left() +self.not_completed_task_times()

    def plot_empty(self):
        fig = plt.figure()
        ax = fig.add_subplot()
        plt.xlim([0, self.len_x])
        plt.ylim([0, self.len_y])
        # tupled = sorted(self.timetable.day_workers.items(), key=operator.itemgetter(1), reverse=True)
        ylabels = []
        for num, worker in enumerate(self.tupled, start=0):
            ylabels.append(worker[0])
            rect = Rectangle((0, num), worker[1], 1, linewidth=1, edgecolor='r')
            ax.add_patch(rect)
        ax.set_yticklabels(ylabels)

        ax.set_title("EmptyPlot")
        plt.show()
        return 0

    def plot(self):
        cmap = plt.cm.get_cmap('hsv', len(self.tasks))
        fig = plt.figure()
        ax = fig.add_subplot()
        plt.xlim([0, self.len_x])
        plt.ylim([0, self.len_y])
        # tupled = sorted(self.timetable.day_workers.items(), key=operator.itemgetter(1), reverse=True)
        ylabels = []
        for num, worker in enumerate(self.tupled, start=0):
            ylabels.append(worker[0])
            rect = Rectangle((0, num), worker[1], 1, linewidth=1, edgecolor='r')
            ax.add_patch(rect)

        ax.set_yticks(np.arange(len(ylabels)))
        ax.set_yticklabels(ylabels)


        for i, task in enumerate(self.tasks):
            for rect in task.rectangles(cmap(i)):
                ax.add_patch(rect)

        ax.set_title("Plot")
        plt.show()
        return 0

    def gravity(self):
        steps = [5,3,1,0.5,0.1]
        for step in steps:
            error = 0
            while error < len(self.tasks):
                error = 0
                for task in self.tasks:
                    best_place = float(task.timelines[0].x)
                    best_intersections = float(self.task_intersections())
                    best_dist = float(self.right_distance())
                    for tl in task.timelines:
                        tl.x = max(0, tl.x -step)
                    # if best_place == 0:
                    #     error += 1


                    if self.task_intersections()+100/self.right_distance() >= best_intersections+100/best_dist: #znak??
                        error += 1
                        # print('step: '+str(step)+", err: "+ str(error))
                        # print(error)
                        for tl in task.timelines:
                            tl.x = best_place

    def zero_gravity(self):
        steps = [20,10,5,3,1,0.5,0.1]
        for step in steps:
            error = 0
            while error < len(self.tasks):
                error = 0
                for task in self.tasks:
                    best_place = float(task.timelines[0].x)
                    best_intersections = float(self.task_intersections())
                    best_dist = float(self.left_distance())
                    for tl in task.timelines:
                        tl.x = min(self.len_x-tl.length, tl.x + step)

                    if self.task_intersections()+100/self.left_distance() >= best_intersections+100/best_dist: #znak??
                        error += 1
                        # print('step: '+str(step)+", err: "+ str(error))
                        # print(error)
                        for tl in task.timelines:
                            tl.x = best_place


    def table_representation(self):

        codes = self.timetable.day_workers.keys()
        load = dict.fromkeys(codes, 0)
        data = {'ID': [], 'Номер задания': [], 'Общее время': [], 'Начать': []}

        for task in self.tasks:
            for tl in task.timelines:
                load[self.code_by_y(tl.y)] += tl.length
                base = 8 * 60
                minutes = tl.x * 60 + base
                hours, minutes = divmod(minutes, 60)
                start_time = "%02d:%02d" % (hours, minutes)
                data['ID'].append(self.code_by_y(tl.y))
                data['Номер задания'].append(task.num)
                data['Общее время'].append(task.duration)
                data['Начать'].append(start_time)

        df = pd.DataFrame(data=data, columns=['ID', 'Номер задания', 'Общее время', 'Начать'])
        # print(df)
        df = df.sort_values(by=['ID', 'Начать'])

        print(df)






