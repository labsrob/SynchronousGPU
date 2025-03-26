# import multiprocessing
#
# # can also be a dictionary
# gpu_id_list = [3, 5, 7, 10]
#
#
# def function(x):
#     cpu_name = multiprocessing.current_process().name
#     cpu_id = int(cpu_name[cpu_name.find('-') + 1:]) - 1
#     gpu_id = gpu_id_list[cpu_id]
#
#     return x * gpu_id
#
#
# if __name__ == '__main__':
#     pool = multiprocessing.Pool(4)
#     input_list = [1, 1, 1, 1]
#     print(pool.map(function, input_list))
# -------------------------------------------------------------
#
import logging
import multiprocessing
import os
import time
#
# # logging just to get not mangled outputs
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#
# def get_process_index(process) -> int:
#     proc_name = multiprocessing.current_process().name
#     # eg. "ForkPoolWorker-10", can be numbered not from zero upon multiple Pool invocations,
#     # be the numbering should be contiguous
#     return int(proc_name.split("-")[1])
#
# def initialize(gpus: list[str]):
#     if gpus:
#         proc_index = get_process_index(multiprocessing.current_process())
#         selected_gpu = gpus[proc_index % len(gpus)]
#         os.environ["CUDA_VISIBLE_DEVICES"] = str(selected_gpu)
#         logger.info(f"process id: {proc_index} -> GPU id: {selected_gpu}")
#
# def work(i):
#     time.sleep(0.1)
#     logger.info(f"work item {i} on GPU {os.environ['CUDA_VISIBLE_DEVICES']}")
#
# available_gpu_ids = [3, 5, 7]
# with multiprocessing.Pool(processes=4, initializer=initialize, initargs=(available_gpu_ids,)) as pool:
#     pool.map(work, range(12))
#
# -----------------------------------------------------------------
#
# from multiprocessing import Pool, current_process, Queue
#
# NUM_GPUS = 4
# PROC_PER_GPU = 2
#
# queue = Queue()
#
# def foo(filename):
#     gpu_id = queue.get()
#     try:
#         # run processing on GPU <gpu_id>
#         ident = current_process().ident
#         print('{}: starting process on GPU {}'.format(ident, gpu_id))
#         # ... process filename
#         print('{}: finished'.format(ident))
#     finally:
#         queue.put(gpu_id)
#
# # initialize the queue with the GPU ids
# for gpu_ids in range(NUM_GPUS):
#     for _ in range(PROC_PER_GPU):
#         queue.put(gpu_ids)
#
# pool = Pool(processes=PROC_PER_GPU * NUM_GPUS)
# files = ['file{}.xyz'.format(x) for x in range(1000)]
# for _ in pool.imap_unordered(foo, files):
#     pass
# pool.close()
# pool.join()

# ----------------------------------------------------------
# import pycuda
# from pycuda import compiler
# import pycuda.driver as drv
#
# drv.init()
# print("%d device(s) found." % drv.Device.count())
#
# for ordinal in range(drv.Device.count()):
#     dev = drv.Device(ordinal)
#     print(ordinal, dev.name())

# --------------------------------------------------------
from tkinter import *
import subprocess
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception: # this command not being found can raise quite a few different errors depending on the configuration
    print('No Nvidia GPU in system!')

# --------------------------------------------------------[]
import json

dictlist = []

import json
json_string = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-1.1273,50.8395,1.0]},"properties":{"location":{"name":"Portchester"},"requestPointDistance":961.7344,"modelRunDate":"2025-03-12T13:00Z","timeSeries":[{"time":"2025-03-12T13:00Z","screenTemperature":7.64,"maxScreenAirTemp":8.15,"minScreenAirTemp":7.6,"screenDewPointTemperature":0.11,"feelsLikeTemperature":4.83,"windSpeed10m":4.55,"windDirectionFrom10m":335,"windGustSpeed10m":6.43,"max10mWindGust":6.45,"visibility":39177,"screenRelativeHumidity":58.76,"mslp":100294,"uvIndex":2,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":6},{"time":"2025-03-12T14:00Z","screenTemperature":6.38,"maxScreenAirTemp":7.64,"minScreenAirTemp":6.34,"screenDewPointTemperature":1.78,"feelsLikeTemperature":3.0,"windSpeed10m":5.11,"windDirectionFrom10m":344,"windGustSpeed10m":6.67,"max10mWindGust":7.83,"visibility":35723,"screenRelativeHumidity":72.43,"mslp":100270,"uvIndex":2,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-12T15:00Z","screenTemperature":6.03,"maxScreenAirTemp":6.38,"minScreenAirTemp":5.97,"screenDewPointTemperature":1.77,"feelsLikeTemperature":3.01,"windSpeed10m":4.22,"windDirectionFrom10m":357,"windGustSpeed10m":5.89,"max10mWindGust":6.53,"visibility":36225,"screenRelativeHumidity":74.03,"mslp":100255,"uvIndex":1,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":9},{"time":"2025-03-12T16:00Z","screenTemperature":6.46,"maxScreenAirTemp":6.47,"minScreenAirTemp":6.03,"screenDewPointTemperature":0.97,"feelsLikeTemperature":3.96,"windSpeed10m":3.49,"windDirectionFrom10m":354,"windGustSpeed10m":5.38,"max10mWindGust":6.02,"visibility":39375,"screenRelativeHumidity":67.91,"mslp":100220,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":2},{"time":"2025-03-12T17:00Z","screenTemperature":6.66,"maxScreenAirTemp":6.8,"minScreenAirTemp":6.46,"screenDewPointTemperature":0.8,"feelsLikeTemperature":4.28,"windSpeed10m":3.45,"windDirectionFrom10m":351,"windGustSpeed10m":5.42,"max10mWindGust":5.97,"visibility":32985,"screenRelativeHumidity":66.27,"mslp":100220,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-12T18:00Z","screenTemperature":5.71,"maxScreenAirTemp":6.66,"minScreenAirTemp":5.69,"screenDewPointTemperature":1.12,"feelsLikeTemperature":3.65,"windSpeed10m":2.67,"windDirectionFrom10m":349,"windGustSpeed10m":5.04,"max10mWindGust":5.6,"visibility":27526,"screenRelativeHumidity":72.3,"mslp":100230,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":4},{"time":"2025-03-12T19:00Z","screenTemperature":5.33,"maxScreenAirTemp":5.71,"minScreenAirTemp":5.23,"screenDewPointTemperature":1.26,"feelsLikeTemperature":3.32,"windSpeed10m":2.53,"windDirectionFrom10m":337,"windGustSpeed10m":5.65,"max10mWindGust":7.81,"visibility":27382,"screenRelativeHumidity":74.99,"mslp":100252,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":6},{"time":"2025-03-12T20:00Z","screenTemperature":5.05,"maxScreenAirTemp":5.33,"minScreenAirTemp":5.02,"screenDewPointTemperature":1.18,"feelsLikeTemperature":2.05,"windSpeed10m":3.83,"windDirectionFrom10m":352,"windGustSpeed10m":8.04,"max10mWindGust":8.38,"visibility":27735,"screenRelativeHumidity":76.09,"mslp":100266,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-12T21:00Z","screenTemperature":4.48,"maxScreenAirTemp":5.05,"minScreenAirTemp":4.46,"screenDewPointTemperature":1.36,"feelsLikeTemperature":1.05,"windSpeed10m":4.26,"windDirectionFrom10m":358,"windGustSpeed10m":8.2,"max10mWindGust":8.67,"visibility":28992,"screenRelativeHumidity":80.18,"mslp":100290,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-12T22:00Z","screenTemperature":3.9,"maxScreenAirTemp":4.48,"minScreenAirTemp":3.89,"screenDewPointTemperature":1.35,"feelsLikeTemperature":0.58,"windSpeed10m":3.86,"windDirectionFrom10m":358,"windGustSpeed10m":7.8,"max10mWindGust":8.55,"visibility":28775,"screenRelativeHumidity":83.43,"mslp":100296,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-12T23:00Z","screenTemperature":3.74,"maxScreenAirTemp":3.99,"minScreenAirTemp":3.68,"screenDewPointTemperature":1.38,"feelsLikeTemperature":0.27,"windSpeed10m":4.07,"windDirectionFrom10m":0,"windGustSpeed10m":8.12,"max10mWindGust":8.51,"visibility":27453,"screenRelativeHumidity":84.67,"mslp":100300,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T00:00Z","screenTemperature":3.4,"maxScreenAirTemp":3.74,"minScreenAirTemp":3.38,"screenDewPointTemperature":1.25,"feelsLikeTemperature":-0.01,"windSpeed10m":3.85,"windDirectionFrom10m":1,"windGustSpeed10m":7.73,"max10mWindGust":8.79,"visibility":28256,"screenRelativeHumidity":85.9,"mslp":100300,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T01:00Z","screenTemperature":3.38,"maxScreenAirTemp":3.44,"minScreenAirTemp":3.35,"screenDewPointTemperature":1.18,"feelsLikeTemperature":-0.15,"windSpeed10m":3.99,"windDirectionFrom10m":1,"windGustSpeed10m":7.83,"max10mWindGust":8.05,"visibility":28070,"screenRelativeHumidity":85.73,"mslp":100300,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T02:00Z","screenTemperature":2.87,"maxScreenAirTemp":3.38,"minScreenAirTemp":2.86,"screenDewPointTemperature":0.97,"feelsLikeTemperature":-0.69,"windSpeed10m":3.91,"windDirectionFrom10m":359,"windGustSpeed10m":7.83,"max10mWindGust":8.29,"visibility":25531,"screenRelativeHumidity":87.4,"mslp":100289,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T03:00Z","screenTemperature":2.57,"maxScreenAirTemp":2.87,"minScreenAirTemp":2.54,"screenDewPointTemperature":0.73,"feelsLikeTemperature":-1.09,"windSpeed10m":3.95,"windDirectionFrom10m":356,"windGustSpeed10m":8.03,"max10mWindGust":8.34,"visibility":24018,"screenRelativeHumidity":87.69,"mslp":100270,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T04:00Z","screenTemperature":2.49,"maxScreenAirTemp":2.57,"minScreenAirTemp":2.48,"screenDewPointTemperature":0.54,"feelsLikeTemperature":-1.56,"windSpeed10m":4.55,"windDirectionFrom10m":1,"windGustSpeed10m":8.63,"max10mWindGust":8.96,"visibility":21743,"screenRelativeHumidity":87.07,"mslp":100271,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T05:00Z","screenTemperature":2.39,"maxScreenAirTemp":2.49,"minScreenAirTemp":2.38,"screenDewPointTemperature":0.47,"feelsLikeTemperature":-1.57,"windSpeed10m":4.39,"windDirectionFrom10m":0,"windGustSpeed10m":8.59,"max10mWindGust":9.04,"visibility":18975,"screenRelativeHumidity":87.32,"mslp":100291,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T06:00Z","screenTemperature":2.17,"maxScreenAirTemp":2.39,"minScreenAirTemp":2.14,"screenDewPointTemperature":0.44,"feelsLikeTemperature":-1.72,"windSpeed10m":4.19,"windDirectionFrom10m":356,"windGustSpeed10m":8.63,"max10mWindGust":8.92,"visibility":18055,"screenRelativeHumidity":88.43,"mslp":100311,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T07:00Z","screenTemperature":2.73,"maxScreenAirTemp":2.74,"minScreenAirTemp":2.17,"screenDewPointTemperature":0.48,"feelsLikeTemperature":-0.76,"windSpeed10m":3.86,"windDirectionFrom10m":349,"windGustSpeed10m":8.11,"max10mWindGust":8.63,"visibility":18892,"screenRelativeHumidity":85.32,"mslp":100340,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T08:00Z","screenTemperature":3.8,"maxScreenAirTemp":3.82,"minScreenAirTemp":2.73,"screenDewPointTemperature":0.69,"feelsLikeTemperature":0.23,"windSpeed10m":4.34,"windDirectionFrom10m":356,"windGustSpeed10m":7.41,"max10mWindGust":7.44,"visibility":26220,"screenRelativeHumidity":80.36,"mslp":100379,"uvIndex":1,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-13T09:00Z","screenTemperature":4.8,"maxScreenAirTemp":4.83,"minScreenAirTemp":3.8,"screenDewPointTemperature":0.6,"feelsLikeTemperature":1.06,"windSpeed10m":5.07,"windDirectionFrom10m":6,"windGustSpeed10m":8.42,"max10mWindGust":8.42,"visibility":34074,"screenRelativeHumidity":74.34,"mslp":100400,"uvIndex":1,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":8},{"time":"2025-03-13T10:00Z","screenTemperature":5.52,"maxScreenAirTemp":5.61,"minScreenAirTemp":4.8,"screenDewPointTemperature":0.63,"feelsLikeTemperature":1.98,"windSpeed10m":5.02,"windDirectionFrom10m":11,"windGustSpeed10m":8.3,"max10mWindGust":8.3,"visibility":35800,"screenRelativeHumidity":70.93,"mslp":100401,"uvIndex":2,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":9},{"time":"2025-03-13T11:00Z","screenTemperature":6.31,"maxScreenAirTemp":6.53,"minScreenAirTemp":5.52,"screenDewPointTemperature":0.41,"feelsLikeTemperature":2.62,"windSpeed10m":5.82,"windDirectionFrom10m":9,"windGustSpeed10m":9.06,"max10mWindGust":9.19,"visibility":37908,"screenRelativeHumidity":66.48,"mslp":100402,"uvIndex":2,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":8},{"time":"2025-03-13T12:00Z","screenTemperature":6.24,"maxScreenAirTemp":6.63,"minScreenAirTemp":6.04,"screenDewPointTemperature":0.6,"feelsLikeTemperature":2.52,"windSpeed10m":5.9,"windDirectionFrom10m":22,"windGustSpeed10m":8.73,"max10mWindGust":8.73,"visibility":25443,"screenRelativeHumidity":67.47,"mslp":100421,"uvIndex":2,"significantWeatherCode":12,"precipitationRate":0.2,"totalPrecipAmount":0.06,"totalSnowAmount":0,"probOfPrecipitation":55},{"time":"2025-03-13T13:00Z","screenTemperature":6.76,"maxScreenAirTemp":6.9,"minScreenAirTemp":5.9,"screenDewPointTemperature":0.31,"feelsLikeTemperature":4.32,"windSpeed10m":3.81,"windDirectionFrom10m":351,"windGustSpeed10m":6.64,"max10mWindGust":6.94,"visibility":32553,"screenRelativeHumidity":64.37,"mslp":100402,"uvIndex":2,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":8},{"time":"2025-03-13T14:00Z","screenTemperature":6.62,"maxScreenAirTemp":7.2,"minScreenAirTemp":6.47,"screenDewPointTemperature":0.25,"feelsLikeTemperature":3.02,"windSpeed10m":6.03,"windDirectionFrom10m":6,"windGustSpeed10m":9.38,"max10mWindGust":9.79,"visibility":37130,"screenRelativeHumidity":64.95,"mslp":100411,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":4},{"time":"2025-03-13T15:00Z","screenTemperature":6.83,"maxScreenAirTemp":6.96,"minScreenAirTemp":6.46,"screenDewPointTemperature":0.06,"feelsLikeTemperature":3.83,"windSpeed10m":4.57,"windDirectionFrom10m":24,"windGustSpeed10m":7.37,"max10mWindGust":9.32,"visibility":34410,"screenRelativeHumidity":62.33,"mslp":100410,"uvIndex":1,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-13T16:00Z","screenTemperature":6.82,"maxScreenAirTemp":7.06,"minScreenAirTemp":6.46,"screenDewPointTemperature":0.42,"feelsLikeTemperature":3.64,"windSpeed10m":5.13,"windDirectionFrom10m":13,"windGustSpeed10m":8.03,"max10mWindGust":9.96,"visibility":32299,"screenRelativeHumidity":63.93,"mslp":100440,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":10},{"time":"2025-03-13T17:00Z","screenTemperature":6.19,"maxScreenAirTemp":6.82,"minScreenAirTemp":6.1,"screenDewPointTemperature":0.57,"feelsLikeTemperature":3.42,"windSpeed10m":3.84,"windDirectionFrom10m":14,"windGustSpeed10m":5.94,"max10mWindGust":7.96,"visibility":37330,"screenRelativeHumidity":67.5,"mslp":100489,"uvIndex":1,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":13},{"time":"2025-03-13T18:00Z","screenTemperature":5.61,"maxScreenAirTemp":6.19,"minScreenAirTemp":5.57,"screenDewPointTemperature":0.94,"feelsLikeTemperature":3.21,"windSpeed10m":3.08,"windDirectionFrom10m":355,"windGustSpeed10m":5.59,"max10mWindGust":6.74,"visibility":34007,"screenRelativeHumidity":72.22,"mslp":100519,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-13T19:00Z","screenTemperature":5.17,"maxScreenAirTemp":5.61,"minScreenAirTemp":5.12,"screenDewPointTemperature":0.94,"feelsLikeTemperature":2.63,"windSpeed10m":3.11,"windDirectionFrom10m":354,"windGustSpeed10m":6.16,"max10mWindGust":7.34,"visibility":33686,"screenRelativeHumidity":74.46,"mslp":100578,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T20:00Z","screenTemperature":4.46,"maxScreenAirTemp":5.17,"minScreenAirTemp":4.41,"screenDewPointTemperature":1.0,"feelsLikeTemperature":1.74,"windSpeed10m":3.19,"windDirectionFrom10m":6,"windGustSpeed10m":6.35,"max10mWindGust":7.71,"visibility":31473,"screenRelativeHumidity":78.63,"mslp":100638,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T21:00Z","screenTemperature":3.83,"maxScreenAirTemp":4.46,"minScreenAirTemp":3.82,"screenDewPointTemperature":1.06,"feelsLikeTemperature":0.95,"windSpeed10m":3.2,"windDirectionFrom10m":5,"windGustSpeed10m":6.4,"max10mWindGust":7.38,"visibility":31001,"screenRelativeHumidity":82.32,"mslp":100679,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T22:00Z","screenTemperature":3.41,"maxScreenAirTemp":3.83,"minScreenAirTemp":3.39,"screenDewPointTemperature":1.12,"feelsLikeTemperature":0.3,"windSpeed10m":3.42,"windDirectionFrom10m":11,"windGustSpeed10m":6.64,"max10mWindGust":7.69,"visibility":30232,"screenRelativeHumidity":85.27,"mslp":100699,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T23:00Z","screenTemperature":2.99,"maxScreenAirTemp":3.41,"minScreenAirTemp":2.95,"screenDewPointTemperature":1.09,"feelsLikeTemperature":-0.11,"windSpeed10m":3.24,"windDirectionFrom10m":9,"windGustSpeed10m":6.59,"max10mWindGust":7.49,"visibility":25988,"screenRelativeHumidity":87.72,"mslp":100701,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T00:00Z","screenTemperature":2.53,"maxScreenAirTemp":2.99,"minScreenAirTemp":2.52,"screenDewPointTemperature":0.87,"feelsLikeTemperature":-0.53,"windSpeed10m":3.1,"windDirectionFrom10m":10,"windGustSpeed10m":6.11,"max10mWindGust":7.62,"visibility":24850,"screenRelativeHumidity":89.1,"mslp":100694,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T01:00Z","screenTemperature":2.16,"maxScreenAirTemp":2.53,"minScreenAirTemp":2.16,"screenDewPointTemperature":0.75,"feelsLikeTemperature":-0.95,"windSpeed10m":3.07,"windDirectionFrom10m":14,"windGustSpeed10m":6.26,"max10mWindGust":7.57,"visibility":23018,"screenRelativeHumidity":90.78,"mslp":100694,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T02:00Z","screenTemperature":1.97,"maxScreenAirTemp":2.16,"minScreenAirTemp":1.93,"screenDewPointTemperature":0.65,"feelsLikeTemperature":-1.16,"windSpeed10m":3.05,"windDirectionFrom10m":13,"windGustSpeed10m":6.05,"max10mWindGust":7.53,"visibility":20691,"screenRelativeHumidity":91.42,"mslp":100693,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T03:00Z","screenTemperature":1.68,"maxScreenAirTemp":1.97,"minScreenAirTemp":1.64,"screenDewPointTemperature":0.25,"feelsLikeTemperature":-1.42,"windSpeed10m":2.94,"windDirectionFrom10m":15,"windGustSpeed10m":6.03,"max10mWindGust":7.63,"visibility":20996,"screenRelativeHumidity":90.55,"mslp":100693,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T04:00Z","screenTemperature":1.46,"maxScreenAirTemp":1.68,"minScreenAirTemp":1.46,"screenDewPointTemperature":0.13,"feelsLikeTemperature":-1.81,"windSpeed10m":3.13,"windDirectionFrom10m":14,"windGustSpeed10m":6.26,"max10mWindGust":8.08,"visibility":19492,"screenRelativeHumidity":91.3,"mslp":100724,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T05:00Z","screenTemperature":1.22,"maxScreenAirTemp":1.46,"minScreenAirTemp":1.21,"screenDewPointTemperature":-0.07,"feelsLikeTemperature":-2.11,"windSpeed10m":3.12,"windDirectionFrom10m":20,"windGustSpeed10m":6.09,"max10mWindGust":8.14,"visibility":18571,"screenRelativeHumidity":91.6,"mslp":100755,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T06:00Z","screenTemperature":0.91,"maxScreenAirTemp":1.31,"minScreenAirTemp":0.85,"screenDewPointTemperature":-0.19,"feelsLikeTemperature":-2.3,"windSpeed10m":2.91,"windDirectionFrom10m":21,"windGustSpeed10m":6.0,"max10mWindGust":7.9,"visibility":7857,"screenRelativeHumidity":92.98,"mslp":100795,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":3},{"time":"2025-03-14T07:00Z","screenTemperature":1.53,"maxScreenAirTemp":1.53,"minScreenAirTemp":0.91,"screenDewPointTemperature":-0.03,"feelsLikeTemperature":-1.4,"windSpeed10m":2.75,"windDirectionFrom10m":21,"windGustSpeed10m":5.86,"max10mWindGust":7.69,"visibility":16810,"screenRelativeHumidity":89.97,"mslp":100846,"uvIndex":1,"significantWeatherCode":1,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T08:00Z","screenTemperature":2.64,"maxScreenAirTemp":2.64,"minScreenAirTemp":1.53,"screenDewPointTemperature":0.32,"feelsLikeTemperature":-0.23,"windSpeed10m":2.92,"windDirectionFrom10m":26,"windGustSpeed10m":5.67,"max10mWindGust":7.29,"visibility":20808,"screenRelativeHumidity":85.21,"mslp":100888,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T09:00Z","screenTemperature":3.82,"maxScreenAirTemp":3.82,"minScreenAirTemp":2.64,"screenDewPointTemperature":0.59,"feelsLikeTemperature":1.06,"windSpeed10m":3.09,"windDirectionFrom10m":28,"windGustSpeed10m":5.42,"max10mWindGust":6.4,"visibility":23621,"screenRelativeHumidity":80.03,"mslp":100930,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T10:00Z","screenTemperature":4.98,"maxScreenAirTemp":4.98,"minScreenAirTemp":3.82,"screenDewPointTemperature":-0.24,"feelsLikeTemperature":2.25,"windSpeed10m":3.48,"windDirectionFrom10m":38,"windGustSpeed10m":6.06,"max10mWindGust":6.06,"visibility":27606,"screenRelativeHumidity":70.01,"mslp":100979,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T11:00Z","screenTemperature":6.04,"maxScreenAirTemp":6.04,"minScreenAirTemp":4.98,"screenDewPointTemperature":-1.28,"feelsLikeTemperature":3.23,"windSpeed10m":3.99,"windDirectionFrom10m":48,"windGustSpeed10m":6.89,"max10mWindGust":6.89,"visibility":31108,"screenRelativeHumidity":60.52,"mslp":101011,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T12:00Z","screenTemperature":6.77,"screenDewPointTemperature":-0.96,"feelsLikeTemperature":3.48,"windSpeed10m":5.59,"windDirectionFrom10m":50,"windGustSpeed10m":8.79,"visibility":25458,"screenRelativeHumidity":58.13,"mslp":101052,"uvIndex":3,"significantWeatherCode":7,"precipitationRate":0.0,"probOfPrecipitation":17},{"time":"2025-03-14T13:00Z","screenTemperature":6.85,"screenDewPointTemperature":-0.69,"feelsLikeTemperature":4.12,"windSpeed10m":4.15,"windDirectionFrom10m":70,"windGustSpeed10m":7.25,"visibility":27266,"screenRelativeHumidity":59.11,"mslp":101099,"uvIndex":2,"significantWeatherCode":7,"precipitationRate":0.0,"probOfPrecipitation":12}]}}],"parameters":[{"totalSnowAmount":{"type":"Parameter","description":"Total Snow Amount Over Previous Hour","unit":{"label":"millimetres","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"mm"}}},"screenTemperature":{"type":"Parameter","description":"Screen Air Temperature","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"visibility":{"type":"Parameter","description":"Visibility","unit":{"label":"metres","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m"}}},"windDirectionFrom10m":{"type":"Parameter","description":"10m Wind From Direction","unit":{"label":"degrees","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"deg"}}},"precipitationRate":{"type":"Parameter","description":"Precipitation Rate","unit":{"label":"millimetres per hour","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"mm/h"}}},"maxScreenAirTemp":{"type":"Parameter","description":"Maximum Screen Air Temperature Over Previous Hour","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"feelsLikeTemperature":{"type":"Parameter","description":"Feels Like Temperature","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"screenDewPointTemperature":{"type":"Parameter","description":"Screen Dew Point Temperature","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"screenRelativeHumidity":{"type":"Parameter","description":"Screen Relative Humidity","unit":{"label":"percentage","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"%"}}},"windSpeed10m":{"type":"Parameter","description":"10m Wind Speed","unit":{"label":"metres per second","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m/s"}}},"probOfPrecipitation":{"type":"Parameter","description":"Probability of Precipitation","unit":{"label":"percentage","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"%"}}},"max10mWindGust":{"type":"Parameter","description":"Maximum 10m Wind Gust Speed Over Previous Hour","unit":{"label":"metres per second","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m/s"}}},"significantWeatherCode":{"type":"Parameter","description":"Significant Weather Code","unit":{"label":"dimensionless","symbol":{"value":"https://datahub.metoffice.gov.uk/","type":"1"}}},"minScreenAirTemp":{"type":"Parameter","description":"Minimum Screen Air Temperature Over Previous Hour","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"totalPrecipAmount":{"type":"Parameter","description":"Total Precipitation Amount Over Previous Hour","unit":{"label":"millimetres","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"mm"}}},"mslp":{"type":"Parameter","description":"Mean Sea Level Pressure","unit":{"label":"pascals","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Pa"}}},"windGustSpeed10m":{"type":"Parameter","description":"10m Wind Gust Speed","unit":{"label":"metres per second","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m/s"}}},"uvIndex":{"type":"Parameter","description":"UV Index","unit":{"label":"dimensionless","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"1"}}}}]}'

data = json.loads(json_string)

print('\nRaw CL Data:', json_string)
print('Loaded Data:', data)
print('\nList Items1:', data.items())

for key, value in data.items():
    temp = [key, value]
    dictlist.append(temp)

print('List Items2:', dictlist)
# print('STRIP', dictlist.strip("[,]"))
# print('\nIndexed Data1:', data['features'])

print('\nIndexed Data1:', (dictlist[1]))        # type
print('Indexed Data2:', (dictlist[1][1]))       # features



def parse(d):
    if isinstance(d, dict):
        return {k: parse(v) for k, v in d.items()
                if k != 'y3' and not
                (isinstance(v, (int, float)) and v > 50)}
    elif isinstance(d, list):
        return [parse(x) for x in d]
    elif isinstance(d, str):
        return f'{d}'
    else:
        return d

out = parse(data)
print('OUT:', out)

# ------------------------------------------------
def printList(l, dict1):
    for l1 in l:
        if dict1.has_key(l1):
            print("withinrange")
        else:
            print("outsiderange")

# file = open("test1.txt")
# textfile = file.readlines()

# dict=dictlist # {'sca4': [['BM1', 17], ['BM2', 33]], 'sca6': [['GM2', 46], ['GM2', 67], ['BM',17]]}

# dict1 = {}
# l =[]
#
# key = ''
# for line in textfile:
#     if not line.strip():
#         continue
#     col1, col2, col3 = line.strip().split(" ")
#     if not (key == col1):
#         printList(l, dict1)
#         l =[]
#         key = col1
#         dict1 = {}
#     for value_list in dict.get(col1, []):
#         #print value_list[1]
#         if not (value_list[1] in l):
#             l.append(value_list[1])
#         if ((int(col2) <= value_list[1]) and (value_list[1] <= int(col3))):
#             dict1[value_list[1]] = 'correct'
#
# printList(l, dictlist)