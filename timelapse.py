import cv2
import time
from datetime import datetime, timedelta
import os
from PIL import Image
import numpy as np
import psutil
import threading
import warnings

import breadboard

images_dir = "/home/heathercraker/Documents/timelapse/images"

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
    '''
    Function to capture an image every 30 seconds or more.
    This minimum time allows the camera to warm up and get a quality image.
    '''
    try:
        # Access the webcam
        cap = cv2.VideoCapture(0)

        # Check if the webcam is opened successfully
        if not cap.isOpened():
            breadboard.errorLED()
            raise Exceptbreadboardn("Failed to open the webcam")
            return

        # Read an image from the webcam
        for i in range(0,30):
            ret, frame = cap.read()

        # Check if the image was successfully captured
        if not ret:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            warnings.warn(f"Failed to capture the image: {now}")
            breadboard.warningLED()
            return

        # Adjust the brightness and contrast of the image
        adjusted_frame = frame
        #adjusted_frame = adjust_brightness(frame, 100)  # Adjust brightness to make the image darker
        #adjusted_frame = adjust_contrast(adjusted_frame, 1.5)  # Adjust contrast
     
        # Generate a human-readable filename with colons replaced by dashes
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{images_dir}/image_{current_time}.jpg"

        # Save the adjusted image
        cv2.imwrite(filename, adjusted_frame)
        
        # Release the webcam
        cap.release()

        print(f"Image captured: {filename}")
        breadboard.successLED()
    finally:
        if cap.isOpened():
            cap.release()



def create_gif(output_file):
    images = []
    
    # Get the list of JPEG files in the image directory
    for filename in os.listdir(images_dir):
        if filename.endswith(".jpg"):
            file_path = os.path.join(images_dir, filename)
            
            # Open each image and append it to the list
            image = Image.open(file_path)
            images.append(image)

    # Save the list of images as an animated GIF
    images[0].save(output_file, save_all=True, append_images=images[1:], loop=0, duration=200)

    print(f"GIF file created: {output_file}")
    breadboard.successLED(3)

def main():
    breadboard.setupIO()

    create_images_dir()

    start_time = datetime.now() # time to start recording images
    end_time = start_time + timedelta(days=1) # time to automatically stop recording
    interval = timedelta(minutes=0) # time between images

    try:
        print("Begin Image Capture")
        previous = datetime.now()
        capture_image()
        while (datetime.now() < end_time) and (not breadboard.buttonStatus()):
            now = datetime.now()
            if (now > start_time) and (now - previous > interval):
                previous = datetime.now()
                capture_image()

        print('Creating timelapse...')
        breadboard.allBlink(0.25, 2)
        start_str = start_time.strftime("%Y-%m-%d_%H-%M")
        end_str = end_time.strftime("%Y-%m-%d_%H-%M")
        gif_filename = f"{images_dir}/timelapse_{start_str}_{end_str}.gif"
        create_gif(gif_filename)
       
        print("Exiting program.")
    finally:
        breadboard.cleanup()
        
if __name__ == '__main__':
    main()
