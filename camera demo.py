import imutils  #Utility functions for OpenCV
import cv2  #OpenCV for image processing
import time  #To handle timestamps for saved videos
import os  #To manage directories

"""
SUMMARY:
This script captures video from a webcam (or other source), detects motion by comparing the difference 
between frames, and records a video when motion is detected AND a recording flag is set to True.
Some doc strings generated with CHATGPT
Reference Code: https://github.com/biplob004/Motion-detection-cv2
"""

#Constants for motion detection sensitivity and persistence
FRAME_UPDATE_INTERVAL = 10  #Number of frames before updating the reference frame
MINIMUM_MOTION_AREA = 5000  #Minimum contour area to be considered motion
MOTION_PERSISTENCE_DURATION = 100  #Number of frames to persist motion before stopping recording / resetting to no motion detected state

#Ensure recordings directory exists
os.makedirs('./recordings', exist_ok=True)

def initialize_video_capture(source=0):
    """Initializes video capture from the given source."""
    return cv2.VideoCapture(source)

def process_frame(frame):
    """Processes a raw video frame for motion detection and display/recording.

    This function takes a color video frame, flips it horizontally, resizes it, and
    prepares two versions: a grayscale blurred version for motion detection and a
    color resized version for display and recording.

    Args:
        frame (numpy.ndarray): The raw input frame in BGR color format (3 channels),
            typically from a video capture source like a webcam or drone camera.

    Returns:
        tuple: A pair of processed frames:
            - blurred (numpy.ndarray): A grayscale, blurred frame (1 channel) for
                motion detection, processed with Gaussian blur to reduce noise.
            - frame_resized (numpy.ndarray): A resized, flipped color frame (3 channels,
                BGR) for display and recording, with annotations added later.

    Steps:
        1. Flips the frame horizontally (left-to-right) to correct orientation.
        2. Resizes the frame to a standard width of 750 pixels.
        3. Converts the resized frame to grayscale for motion detection.
        4. Applies Gaussian blur to the grayscale frame to smooth out noise.
    """
    frame = cv2.flip(frame, 1)
    frame_resized = imutils.resize(frame, width=750)  #Resize the frame to standard width
    grayscale = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  #Convert to grayscale
    blurred = cv2.GaussianBlur(grayscale, (21, 21), 0)  #Apply Gaussian blur to reduce noise
    return blurred, frame_resized  #Return processed frames

def detect_motion(reference_frame, current_frame):
    """Detects motion by analyzing differences between a reference frame and the current frame.

    This function computes the absolute difference between two grayscale frames, applies a binary
    threshold to highlight significant changes, dilates the result to enhance motion regions, and
    identifies contours that represent potential motion.

    Args:
        reference_frame (numpy.ndarray): The grayscale reference frame (1 channel) used as a baseline
            for motion detection. Typically the first frame or periodically updated.
        current_frame (numpy.ndarray): The grayscale current frame (1 channel) to compare against
            the reference frame.

    Returns:
        list: A list of contours (numpy.ndarray) representing regions of detected motion. Each contour
            is an array of points outlining a moving object.

    Steps:
        1. Compute the absolute difference between the reference and current frames.
        2. Apply a binary threshold to isolate significant changes (intensity > 25).
        3. Dilate the thresholded image to fill gaps and enhance motion regions.
        4. Find external contours in the dilated image to identify motion areas.
    """
    frame_difference = cv2.absdiff(reference_frame, current_frame)  #Find differences between frames
    threshold_frame = cv2.threshold(frame_difference, 25, 255, cv2.THRESH_BINARY)[1]  #Apply binary threshold
    threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)  #Dilate to fill small holes
    contours, _ = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  #Find contours
    return contours  #Return detected contours (potential motion regions)

def motion_detection_loop():
    """Runs the main loop to capture video, detect motion, record video when conditions are met, and handle user input.

    This function initializes a video capture device, processes frames to detect motion, displays the video feed with
    annotations, and records video to a file when motion is detected and the recording flag is True. It also allows
    toggling recording with 'r' and exiting with 'q'. Resources are cleaned up upon exit.

    Args:
        None

    Returns:
        None

    Steps:
        1. Initialize video capture and set up variables for motion tracking and recording.
        2. Enter a loop to continuously capture and process frames.
        3. Detect motion by comparing the current frame to a reference frame.
        4. Annotate the processed frame with bounding boxes and status text if motion is detected.
        5. Record video if motion persists and recording is enabled.
        6. Stop recording and release resources when motion ceases or the user exits.
        7. Handle keypresses to toggle recording ('r') or exit ('q').
        8. Clean up video capture and writer objects upon loop exit.
    """
    video_capture = initialize_video_capture()
    reference_frame = None  #Store the initial reference frame for motion detection
    motion_persistence_counter = 0  #Keeps track of how long motion is detected
    frame_update_counter = 0  #Counter to update the reference frame periodically
    font_style = cv2.FONT_HERSHEY_SIMPLEX  #Font style for overlay text
    video_writer = None  #Placeholder for video writer
    video_codec = cv2.VideoWriter_fourcc(*'XVID')  #Video codec for recording output
    
    recording = False  #Flag to control video recording
    announced_detected_motion = False #Flag that tells if motion has been announced to user
    
    try:
        while True:
            motion_detected = False  #Flag to indicate motion presence
            ret, frame = video_capture.read()  #Capture the current frame
            if not ret:
                print("CAPTURE ERROR: Could not read frame")
                continue
    
            current_frame, processed_frame = process_frame(frame)  #Process the frame
            
            if reference_frame is None:
                reference_frame = current_frame  #Set the first reference frame
            
            frame_update_counter += 1
            if frame_update_counter > FRAME_UPDATE_INTERVAL:
                frame_update_counter = 0
                reference_frame = current_frame  #Update reference frame 
            
            motion_contours = detect_motion(reference_frame, current_frame)  #Detect motion in the frame
            for contour in motion_contours:
                if cv2.contourArea(contour) > MINIMUM_MOTION_AREA:  #Only consider large enough motion
                    motion_detected = True
                    (x, y, width, height) = cv2.boundingRect(contour)  #Get bounding box
                    cv2.rectangle(processed_frame, (x, y), (x + width, y + height), (0, 255, 0), 2)  #Draw rectangle
                    
            if motion_detected and not announced_detected_motion:
                announced_detected_motion = True
                print("New Motion Detected")
            
            if motion_detected:
                motion_persistence_counter = MOTION_PERSISTENCE_DURATION  #Reset persistence timer when motion detected
            
            
            #Add recording status to text 
            if motion_persistence_counter > 0:
                motion_status_text = f"Motion Detected ({motion_persistence_counter}) - Recording: {recording}" 
            else:
                motion_status_text = f"No Motion Detected - Recording: {recording}"
                
            motion_persistence_counter = max(0, motion_persistence_counter - 1)  #Decrease counter until zero
            cv2.putText(processed_frame, motion_status_text, (10, 35), font_style, 0.75, (255, 255, 255), 2, cv2.LINE_AA)  #Overlay text
            cv2.imshow("Motion Detection", processed_frame)  #Show the processed frame
        
            #Only initialize video writer if recording flag is True
            if motion_persistence_counter > 0 and not video_writer and recording:
                frame_height, frame_width, _ = frame.shape  #Get frame dimensions
                video_writer = cv2.VideoWriter(f'./recordings/{int(time.time())}_motion_video.avi', video_codec, 25.0, (frame_width, frame_height))  #Initialize video writer
            
            #Only write to video if recording flag is True
            if motion_persistence_counter > 0 and video_writer and recording:
                video_writer.write(frame)  #Save frame to video file
            
            if motion_persistence_counter == 0 and video_writer:
                video_writer.release()  #Stop recording
                video_writer = None
                
            if motion_persistence_counter == 0: #Resets announced_detected_motion to False so new movement will be noticed
                announced_detected_motion = False
            
            #Toggle recording flag with 'r'
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  #Exit when 'q' is pressed
                if video_writer:
                    video_writer.release()  #Ensure video writer is properly closed
                break  #Exit loop
            elif key == ord('r'):  #Toggle recording with 'r'
                recording = not recording
                print(f"Recording set to: {recording}")
    
    finally:  #Ensures cleanup happends
        print("Releasing video capture...")
        video_capture.release()
        if video_writer:
            print("Releasing video writer...")
            video_writer.release()
        print("Closing all windows...")
        cv2.destroyAllWindows()
        print("Cleanup complete.")
    
if __name__ == "__main__":
    #Run the motion detection loop
    motion_detection_loop()