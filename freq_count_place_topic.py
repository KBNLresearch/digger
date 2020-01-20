#!/usr/bin/env python3.5

import requests
import json
from lxml import etree
import time
import random
import threading

SRU_QUERY = 'http://jsru.kb.nl/sru/sru?query='
SRU_QUERY += '"%s" and "%s" and ppn exact "%s" '
SRU_QUERY += 'and date within "01-01-%s 31-12-%s" '
SRU_QUERY += 'and type exact "%s"'
SRU_QUERY += '&x-collection=DDD_artikel&maximumRecords=1'
SRU_QUERY += '&startRecord=%s'

WANTED_TOPICS = []
WANTED_PLACES = []
WANTED_PPNS = []
WANTED_RANGES = []
WANTED_TYPES = ["illustratie met onderschrift",
                "artikel",
                "advertentie",
                "familiebericht"]

def read_ppns(filename='ppn.csv'):
    global WANTED_PPNS

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        ppn = line[1:-1]
        WANTED_PPNS.append(ppn)

def read_places(filename='places.csv'):
    global WANTED_PLACES

    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        place = line.split(',')[0][1:-1]
        WANTED_PLACES.append(place)

def read_years(filename='years.txt'):
    global WANTED_RANGES
    years = []


    '''
    with open(filename) as fh:
        data = fh.read()

    for line in data.split('\n'):
        if not line == 'Years':
            years.append(str(line))

    for i in range(0, len(years)-1):
        if i >0:
            WANTED_RANGES.append([str(int(years[i]) + 1), years[i + 1]])
        else:
            WANTED_RANGES.append([years[i], years[i+1]])
    '''

    for i in range(1865, 1995):
        WANTED_RANGES.append(str(i))

def exec_query(topic, ppn, place, date, atype):
    done = False

    while not done:
        date_start = date_end = date
        #date_start = str(int(date_start))
        sru = SRU_QUERY % (topic, place, ppn, date_start, date_end, atype, '0')
        try:
            data = requests.get(sru)
            data = etree.fromstring(data.content)
            done = True

        except:
            time.sleep(random.random())

    for item in data.iter():
        if item.tag.endswith('numberOfRecords'):
            return item.text

def read_topics(fname='categories.txt'):
    global WANTED_TOPICS
    cat = {}
    all_topics = []
    with open(fname, 'r') as fh:
        for line in fh.read().split('\n'):
            if not line:
                continue
            name = line.split(',')[0]
            if not line.split(',')[1].isupper():
                if not name in cat:
                    cat[name] = []
                cat[name].append(line.split(',')[1])
                all_topics.append(line.split(',')[1])
    WANTED_TOPICS = all_topics

def do_one_topic(topic, outfile):
    for ppn in WANTED_PPNS:
        for place in WANTED_PLACES:
            for date in WANTED_RANGES:
                for atype in WANTED_TYPES:
                    result.append((topic,
                                   ppn,
                                   place,
                                   date,
                                   atype,
                                   exec_query(topic,
                                              ppn,
                                              place,
                                              date,
                                              atype,
                                              )
                                   ))
                    out = str(result[-1])[1:-1] + '\n'
                    outfile.write(out)


class myThread(threading.Thread):
    def __init__(self, topic):
        threading.Thread.__init__(self)
        self.topic = topic

    def run(self):
        with open(topic + ".csv", 'a') as fh:
            do_one_topic(topic, fh)


if __name__ == '__main__':
    read_ppns()
    read_places()
    read_years()
    read_topics()

    result = []

    running_threads = []

    for topic in WANTED_TOPICS:
        thread = myThread(topic)
        thread.start()
        running_threads.append(thread)

    for t in running_threads:
        t.join()
'''

output:

    37631091X Eindhoven 1900 1909 2068

    ppn, place, start_date, end_date, freq



#!/usr/bin/python3

import threading
import time

exitFlag = 0

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      print ("Starting " + self.name)
      print_time(self.name, self.counter, 5)
      print ("Exiting " + self.name)

def print_time(threadName, delay, counter):
   while counter:
      if exitFlag:
         threadName.exit()
      time.sleep(delay)
      print ("%s: %s" % (threadName, time.ctime(time.time())))
      counter -= 1

# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print ("Exiting Main Thread")





'''
