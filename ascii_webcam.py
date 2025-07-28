import cv2
import numpy as np
import os
import keyboard
import time

# ASCII characters from darkest to lightest
ASCII_CHARS = "@%#*+=-:. "

def resize_frame(frame, new_width=100):
    """
    Resizes a frame to a new width while maintaining the aspect ratio.
    """
    (old_height, old_width) = frame.shape
    aspect_ratio = old_height / float(old_width)
    new_height = int(aspect_ratio * new_width * 0.55) # 0.55 is a correction factor for character aspect ratio
    resized_frame = cv2.resize(frame, (new_width, new_height))
    return resized_frame

def grayscale(frame):
    """
    Converts a frame to grayscale.
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def adapt_brightness(frame):
    """
    Adapts the brightness of the frame using histogram equalization.
    This helps in making the subject clearer in varying light conditions.
    """
    return cv2.equalizeHist(frame)

def frame_to_ascii(frame, ascii_chars):
    """
    Converts a grayscale frame to an ASCII string.
    """
    pixels = frame.flatten()
    # Map each pixel intensity (0-255) to an ASCII character index (0-9)
    # The formula `pixel * len(ascii_chars) // 256` correctly scales the range.
    ascii_str = "".join([ascii_chars[pixel * len(ascii_chars) // 256] for pixel in pixels])
    return ascii_str

def main():
    """
    Main function to capture video from webcam and display it as ASCII art.
    """
    # Attempt to open the default webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break

            # --- Frame Processing ---
            # 1. Convert to grayscale
            gray_frame = grayscale(frame)

            # 2. Adapt brightness
            bright_frame = adapt_brightness(gray_frame)

            # 3. Resize for terminal display
            resized_frame = resize_frame(bright_frame)

            # 4. Convert to ASCII
            (height, width) = resized_frame.shape
            ascii_str = frame_to_ascii(resized_frame, ASCII_CHARS)

            # --- Displaying the ASCII art ---
            # Clear the console
            os.system('cls' if os.name == 'nt' else 'clear')

            # Print ASCII string line by line
            for i in range(0, len(ascii_str), width):
                print(ascii_str[i:i+width])

            # --- Exit Conditions ---
            # Check for 'q' or 'esc' key press
            if keyboard.is_pressed('q') or keyboard.is_pressed('esc'):
                print("Exiting...")
                break
            
            # A short delay to control frame rate
            time.sleep(0.05)


    except KeyboardInterrupt:
        print("\nExiting due to Ctrl+C...")
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
