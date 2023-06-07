import cv2
import time
from datetime import datetime
import os
from PIL import Image
import numpy as np
import psutil
import threading

#''' Process Monitoring
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

images_dir = "C:/Users/heath/OneDrive/Personal Projects/Timelapse/images"

def create_images_dir(dir=None):
    global images_dir
    if dir:
        images_dir = dir
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"Directory created: {images_dir}")
    else:
        print(f"Directory already exists: {images_dir}")

def adjust_brightness(image, value):
    # Convert the image to the LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split the LAB channels
    l, a, b = cv2.split(lab)
    
    # Adjust the L channel (brightness)
    l = cv2.add(l, value)
    
    # Clip the values to the valid range of 0-255
    l = np.clip(l, 0, 255)
    
    # Merge the LAB channels back together
    adjusted_lab = cv2.merge((l, a, b))
    
    # Convert back to the BGR color space
    adjusted_image = cv2.cvtColor(adjusted_lab, cv2.COLOR_LAB2BGR)
    
    return adjusted_image

def adjust_contrast(image, value):
    # Convert the image to the LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split the LAB channels
    l, a, b = cv2.split(lab)
    
    # Adjust the L channel (contrast)
    l = cv2.multiply(l, value)
    
    # Clip the values to the valid range of 0-255
    l = np.clip(l, 0, 255)
    
    # Merge the LAB channels back together
    adjusted_lab = cv2.merge((l, a, b))
    
    # Convert back to the BGR color space
    adjusted_image = cv2.cvtColor(adjusted_lab, cv2.COLOR_LAB2BGR)
    
    return adjusted_image

def capture_image():
    # Access the webcam
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Failed to open the webcam")
        return

    # Read an image from the webcam
    for i in range(0,30):
        ret, frame = cap.read()

    # Check if the image was successfully captured
    if not ret:
        print("Failed to capture the image")
        return

    # Adjust the brightness and contrast of the image
    adjusted_frame = frame
    #adjusted_frame = adjust_brightness(frame, 100)  # Adjust brightness to make the image darker
    #adjusted_frame = adjust_contrast(adjusted_frame, 1.5)  # Adjust contrast
 
    # Generate a human-readable filename with colons replaced by dashes
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{images_dir}/image_{current_time}.png"

    # Save the adjusted image
    cv2.imwrite(filename, adjusted_frame)

    # Release the webcam
    cap.release()

    print(f"Image captured: {filename}")

def create_gif(output_file):
    images = []
    
    # Get the list of JPEG files in the image directory
    for filename in os.listdir(images_dir):
        if filename.endswith(".png"):
            file_path = os.path.join(images_dir, filename)
            
            # Open each image and append it to the list
            image = Image.open(file_path)
            images.append(image)

    # Save the list of images as an animated GIF
    images[0].save(output_file, save_all=True, append_images=images[1:], loop=0, duration=200)

    print(f"GIF file created: {output_file}")

def main():
    create_images_dir()

    monitor_thread = None
    start_time = datetime.now()#(2023, 6, 7, 4, 0, 0) # time to start recording images
    end_time = datetime(2023,6,7,18,0,0)
    try:
        # Start monitoring memory usage in a separate thread
        #monitor_thread = MemoryMonitorThread()
        #monitor_thread.start()
        print("Begin Image Capture")
        while datetime.now() < end_time:
            if datetime.now() > start_time:
                capture_image()
            time.sleep(60*5) # Wait

        print('Creating timelapse...')
        start_str = start_time.strftime("%Y-%m-%d")
        end_str = end_time.strftime("%Y-%m-%d")
        gif_filename = f"./timelapse_{start_str}_{end_str}.gif"
        create_gif(gif_filename)

    except KeyboardInterrupt:
        print('Keyboard Interrupt!')
        
        print('Creating timelapse...')
        start_str = start_time.strftime("%Y-%m-%d_%H-%M")
        end_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        gif_filename = f"./timelapse_{start_str}_{end_str}.gif"
        create_gif(gif_filename)
        
        print("Cleaning up...")
        #if monitor_thread is not None:
        #            monitor_thread.stop()  # Signal the monitoring thread to stop
        #            monitor_thread.join()  # Wait for the monitoring thread to finish
        print("Exiting program.")
        
if __name__ == '__main__':
    main()
