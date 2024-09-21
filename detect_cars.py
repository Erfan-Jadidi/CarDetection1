import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import ffmpeg
import os
import datetime
import pytz
from scipy.signal import find_peaks
import sqlite3

def convert_to_canada_time(local_time, local_timezone_str, canada_timezone_str):
    local_timezone = pytz.timezone(local_timezone_str)
    local_time = local_timezone.localize(local_time)
    canada_timezone = pytz.timezone(canada_timezone_str)
    canada_time = local_time.astimezone(canada_timezone)
    return canada_time

def get_file_creation_time(file_path):
    creation_time = os.path.getctime(file_path)
    creation_time_readable = datetime.datetime.fromtimestamp(creation_time)
    date = creation_time_readable.date()
    time = creation_time_readable.time().replace(microsecond=0)
    full_creation_time = datetime.datetime.combine(date, time)
    return full_creation_time

vid_path = "F:\\DA\\Projects\\Peace_bridge\\output3.mp4"
vid_cv = cv.VideoCapture(vid_path)

if not vid_cv.isOpened():
    print(f"Error: Could not open video file: {vid_path}")
    exit()

# Time
main_time = get_file_creation_time(vid_path)
local_timezone_str = 'Asia/Tehran'
canada_timezone_str = 'America/Toronto'
canada_time = convert_to_canada_time(main_time, local_timezone_str, canada_timezone_str)

# Lines Detections
fps = vid_cv.get(cv.CAP_PROP_FPS)
num_frames_to_process = int(fps * 180)
frame_count = 0

# Initialize lists for storing differences and timestamps
lst = []
timestamps = []

ret, frame1 = vid_cv.read()
if not ret or frame1 is None:
    print("Error: Could not read the first frame from the video.")
    exit()

# Line1 processing
image = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
pts = np.array([[400, 491], [335, 560], [551, 560], [559, 491]])
mask = np.zeros(image.shape[:2], dtype=np.uint8)
cv.fillPoly(mask, [pts], 255)
trapezoid_region = cv.bitwise_and(image, image, mask=mask)
main_mask = trapezoid_region

while vid_cv.isOpened() and frame_count < num_frames_to_process:
    ret, frame2 = vid_cv.read()
    if not ret or frame2 is None:
        break
    
    gray = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)

    # Line1 processing
    mask = np.zeros(gray.shape[:2], dtype=np.uint8)
    cv.fillPoly(mask, [pts], 255)
    trapezoid_regions = cv.bitwise_and(gray, gray, mask=mask)
    diff = cv.absdiff(main_mask, trapezoid_regions)
    main_mask = trapezoid_regions.copy()
    diff_sum = pow(np.sum(diff), 2)
    lst.append(diff_sum)


    current_time = datetime.timedelta(seconds=frame_count / fps)
    timestamps.append(current_time)
    
    cv.imshow('line1', trapezoid_regions)
    
    if cv.waitKey(30) & 0xFF == ord('q'):
        break
    
    frame_count += 1

vid_cv.release()
cv.destroyAllWindows()

# Car Number Line1
peaks, _ = find_peaks(lst, height=1e11, distance=100, prominence=1e11)

plt.figure()
plt.plot(np.ravel(lst))
plt.plot(peaks, np.array(lst)[peaks], "x")
plt.title('Line 1 Car Detection')
plt.show()

print(f"Number of peaks detected for Line 1: {len(peaks)}")
# sqlite
conn = sqlite3.connect('NewData.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        value INTEGER NOT NULL
    )
''')

cnt_car = 0

if len(timestamps) == len(lst):
    for peak in peaks:
        if peak < len(timestamps):
            cnt_car += 1
            peak_time = timestamps[peak]
            total_seconds = peak_time.total_seconds()
            detection_time = canada_time + datetime.timedelta(seconds=total_seconds)
            formatted_time = detection_time.strftime('%Y-%m-%d %H:%M:%S')
            current_time = formatted_time
            cursor.execute('''
                INSERT INTO records (timestamp, value)
                VALUES (?, ?)
                ''', (current_time, cnt_car))
else:
    print("Error: Length of timestamps list does not match length of lst.")

conn.commit()
conn.close()