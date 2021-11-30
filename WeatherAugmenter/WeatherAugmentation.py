import os
import sys
import ssl
import json
import time
import shutil
import multiprocessing

from pathlib import Path
from GeoWeather import GeoWeatherService

INPUT_FOLDER = 'INPUT'
PROCESSED_FOLDER = 'PROCESSED'
OUTPUT_FOLDER = 'OUTPUT'

MAX_FILE_ATTEMPT_TIME = 5 * 60
REATTEMPT_SLEEP_INTERVAL = 1.0

def main():
    
    Path(PROCESSED_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    filenames = os.listdir(INPUT_FOLDER)
    process_files(filenames)
    
def augment_weather(record, geo_weather_service):
    date = record['Occurrence Summary'][0]['Date']
    location = record['Occurrence Location:']
    aerodrome = record['Canadian Aerodrome ID:']
    province = record['Province:']
    country = record['Country:']
    
    coords, weather = geo_weather_service.retrieve_data(date, aerodrome, location, province, country)
    
    record['latitude'] = coords.latitude
    record['longitude'] = coords.longitude
    record['weather'] = weather.to_dict('records')[0]
    
def handle_augment_fail(record):
    record['latitude'] = None
    record['longitude'] = None
    record['weather'] = {}

def file_thread(i, file):

    ws = GeoWeatherService()

    try:
        src = os.path.join(INPUT_FOLDER, str(file))
        dst = os.path.join(PROCESSED_FOLDER, str(file))

        with open(os.path.join(INPUT_FOLDER, file)) as f:
            data = json.load(f)

    except Exception as e:
        print('\n> Unable to open, skipping file #', str(i + 1), end='')
        return
    
    print('\nProcessing file #' + str(i + 1), end=' ')
    
    for j in range(len(data)):
        
        try:
            augment_weather(data[j], ws)
            print('.', end='')
            
        except Exception as e:
            time.sleep(REATTEMPT_SLEEP_INTERVAL)
            try:
                augment_weather(data[j], ws)
                print('.', end='')
                
            except Exception as e:
                #print('Error processing record', str(e))
                handle_augment_fail(data[j])
                print('_', end='')

        sys.stdout.flush()
                            
    try:      
        with open(os.path.join(OUTPUT_FOLDER, 'wx-' + str(file)), 'w') as f:
            json.dump(data, f)

        shutil.move(src=src, dst=dst)

    except Exception as e:
        print('\n> Unable to write to output file, the input file will not be moved', end ='')
        return

def process_files(filenames):
        
    for (i, file) in enumerate(filenames):

        process = multiprocessing.Process(target=file_thread, args=[i, file])
        process.start()
        process.join(timeout=MAX_FILE_ATTEMPT_TIME)
        
        # If process is not completed by time limit, terminate it
        if process.is_alive():

            print('\n> Maximum time limit exceeded, skipping file #' + str(i + 1), end='')
            process.kill()
            time.sleep(REATTEMPT_SLEEP_INTERVAL)
            
    print('>>> Task completed, all files are processed!')

if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    main()