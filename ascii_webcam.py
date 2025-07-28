import cv2
import numpy as np
import os
import keyboard
import time
import shutil
from PIL import Image, ImageDraw, ImageFont
import msvcrt

# ASCII characters from darkest to lightest
ASCII_CHARS = " .:-=+*#%@"

def get_terminal_size():
    """
    Gets the size of the terminal.
    """
    return shutil.get_terminal_size(fallback=(100, 30)) # Default to 100x30 if detection fails

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
    Adapts the brightness of the frame using Contrast Limited Adaptive Histogram Equalization (CLAHE).
    This helps in making the subject clearer in varying light conditions.
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(frame)

def invert_brightness(frame):
    """
    Inverts the brightness of the frame.
    """
    return cv2.bitwise_not(frame)

def frame_to_ascii(frame, ascii_chars):
    """
    Converts a grayscale frame to an ASCII string.
    """
    pixels = frame.flatten()
    # Map each pixel intensity (0-255) to an ASCII character index (0-9)
    # The formula `pixel * len(ascii_chars) // 256` correctly scales the range.
    ascii_str = "".join([ascii_chars[pixel * len(ascii_chars) // 256] for pixel in pixels])
    return ascii_str

def save_as_png(ascii_str, width, height):
    """
    Saves the ASCII art as a PNG image.
    """
    # Create a directory for screenshots if it doesn't exist
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Set image dimensions and font
    font = ImageFont.load_default()
    char_width, char_height = font.getsize('A')
    img_width = width * char_width
    img_height = height * char_height

    # Create a new image
    img = Image.new('RGB', (img_width, img_height), color='black')
    d = ImageDraw.Draw(img)

    # Draw the ASCII text onto the image
    for i in range(height):
        line = ascii_str[i*width:(i+1)*width]
        d.text((0, i*char_height), line, fill='white', font=font)

    # Save the image
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filepath = os.path.join('screenshots', f'ascii_screenshot_{timestamp}.png')
    img.save(filepath)
    print(f"Screenshot saved to {filepath}")

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
        brightness_inverted = False
        while True:
            terminal_width, _ = get_terminal_size()
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

            # Check for brightness inversion key press
            if keyboard.is_pressed('d'):
                brightness_inverted = not brightness_inverted
                time.sleep(0.2) # Debounce key press

            if brightness_inverted:
                bright_frame = invert_brightness(bright_frame)

            # 3. Resize for terminal display
            resized_frame = resize_frame(bright_frame, new_width=terminal_width)

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
            # Check for screenshot key press
            if keyboard.is_pressed('s'):
                save_as_png(ascii_str, width, height)
                time.sleep(0.2) # Debounce key press

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
        # Clear any buffered key presses
        while msvcrt.kbhit():
            msvcrt.getch()
        

if __name__ == "__main__":
    main()