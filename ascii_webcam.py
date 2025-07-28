import cv2
import os
import shutil
import numpy as np

########################################################################
# SETTINGS #
SHOW_REAL_VIDEO = True   # Set this to True to get real camera video from cv2
USE_EXTENDED_CHARS = True  # Use extended character set for better quality
ASPECT_RATIO_CORRECTION = 1.0  # Adjust for character aspect ratio (height/width)
########################################################################

def convert_row_to_ascii(row, extended=False):
    if extended:
        # Extended 32-character set for much better detail
        ORDER = (' ', '`', '.', "'", ',', ':', ';', '^', '"', '~', '-', '_', 
                '+', '=', '<', '>', 'i', '!', 'l', 'I', '?', '/', '\\', '|',
                '(', ')', '1', '{', '}', '[', ']', 'r', 'c', 'v', 'u', 'n',
                'x', 'z', 'j', 'f', 't', 'L', 'C', 'J', 'U', 'Y', 'X', 'Z',
                'O', '0', 'Q', 'o', 'a', 'h', 'k', 'b', 'd', 'q', 'p', 'w',
                'm', 'W', 'B', '8', '&', '%', '$', '#', '@')
        # 64 characters total
    else:
        # Original 17-character set
        ORDER = (' ', '.', "'", ',', ':', ';', 'c', 'l',
                 'x', 'o', 'k', 'X', 'd', 'O', '0', 'K', 'N')
    
    max_index = len(ORDER) - 1
    return tuple(ORDER[min(int(x * max_index / 255), max_index)] for x in row)

def convert_to_ascii(input_grays, extended=False):
    return tuple(convert_row_to_ascii(row, extended) for row in input_grays)

def print_array(input_ascii_array):
    # Use ANSI escape codes for better clearing
    print('\033[2J\033[H', end='')  # Clear screen and move cursor to top
    print('\n'.join((''.join(row) for row in input_ascii_array)), end='', flush=True)

def apply_contrast_enhancement(image, alpha=1.2, beta=10):
    """Apply contrast and brightness adjustment"""
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def apply_histogram_equalization(image):
    """Apply histogram equalization for better contrast"""
    return cv2.equalizeHist(image)

def main():
    cap = cv2.VideoCapture(0)
    
    # Set camera properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("ASCII Webcam started. Press 'q' or 'ESC' to quit.")
    
    try:
        while True:
            # Check for key press (non-blocking)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC key
                break
            
            # Get screensize for reduction
            screen_size = shutil.get_terminal_size((80, 24))
            screen_width, screen_height = screen_size.columns, screen_size.lines
            
            # Adjust for aspect ratio - characters are taller than wide
            adjusted_height = int(screen_height / ASPECT_RATIO_CORRECTION)
            
            # Get image data
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply image enhancements
            enhanced = apply_contrast_enhancement(gray)
            enhanced = apply_histogram_equalization(enhanced)
            
            # Apply Gaussian blur to reduce noise
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # Resize with better interpolation
            reduced = cv2.resize(enhanced, (screen_width, adjusted_height), 
                               interpolation=cv2.INTER_AREA)
            
            # Convert to ASCII
            converted = convert_to_ascii(reduced, USE_EXTENDED_CHARS)
            print_array(converted)
            
            # Display the real video if enabled
            if SHOW_REAL_VIDEO:
                cv2.imshow('Enhanced Frame', enhanced)
                cv2.imshow('Original Frame', gray)
                
                # Check for window close button
                if cv2.getWindowProperty('Enhanced Frame', cv2.WND_PROP_VISIBLE) < 1:
                    break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("\nCamera released and windows closed.")

if __name__ == "__main__":
    main()