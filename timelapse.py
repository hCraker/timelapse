import cv2
import time
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import os
from PIL import Image
import numpy as np
import psutil
import threading
import warnings

''' Process Monitoring
class MemoryMonitorThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            # Retrieve memory usage information
            memory_info = psutil.virtual_memory()

            # Print memory usage statistics
            print(f"Total: {memory_info.total} bytes")
            print(f"Available: {memory_info.available} bytes")
            print(f"Used: {memory_info.used} bytes")
            print(f"Percentage: {memory_info.percent}%\n")

            # Sleep for a specific interval (e.g., 1 second)
            time.sleep(1)
#'''

images_dir = f"C:/Users/heath/OneDrive/Personal Projects/Timelapse/{int(time.mktime(datetime.now().timetuple()))}"

start_time = datetime.now() #datetime(2023, 9, 8, 8, 30)
duration = timedelta(minutes=1)
end_time = start_time + duration
interval = 0.05 # interval between pictures in minutes

def create_images_dir(dir=None):
    global images_dir
    if dir:
        images_dir = dir
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Directory created: {images_dir}")
    else:
        print(f"Directory already exists: {images_dir}")

def capture_image():    
    # Access the webcam
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print(f"Failed to open the webcam at {datetime.now()}")
        return

    # Turn on camera capture
    cap.read()
    # Wait for camera warmup
    time.sleep(1)
    # Read an image from the webcam
    ret, frame = cap.read()

    # Check if the image was successfully captured
    if not ret:
        print(f"Failed to capture the image at {datetime.now()}")
        return
 
    # Generate a human-readable filename with colons replaced by dashes
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{images_dir}/image_{current_time}.png"

    # Save the image
    cv2.imwrite(filename, frame)

    # Release the webcam
    cap.release()

    print(f"Image captured: {filename}")

def create_gif(start_time):
    print('Creating timelapse...')
    start_str = start_time.strftime("%Y-%m-%d--%H-%M")
    end_str = datetime.now().strftime("%Y-%m-%d--%H-%M")
    output_file = f"{images_dir}/timelapse_{start_str}_{end_str}.gif"
    
    images = []
    
    # Get the list of JPEG files in the image directory
    for filename in os.listdir(images_dir):
        if filename.endswith(".jpg"):
            file_path = os.path.join(images_dir, filename)
            
            # Open each image and append it to the list
            image = Image.open(file_path)
            images.append(image)

    # Save the list of images as an animated GIF
    images[0].save(output_file, format="GIF", append_images=images[1:], save_all=True, duration=200, loop=0)

    print(f"GIF file created: {output_file}")


def main():

    create_images_dir()

    monitor_thread = None

    try:
        print("Begin Image Capture")
        while datetime.now() > start_time:
            if datetime.now() < end_time:
                capture_image()
            else:
                break 
            time.sleep(60*interval) # Wait

        create_gif(start_time)

    except KeyboardInterrupt:
        print('Keyboard Interrupt!')
        
        create_gif(start_time)
        
        print("Cleaning up...")
        #if monitor_thread is not None:
        #            monitor_thread.stop()  # Signal the monitoring thread to stop
        #            monitor_thread.join()  # Wait for the monitoring thread to finish
        print("Exiting program.")

        
if __name__ == '__main__':
    main()
