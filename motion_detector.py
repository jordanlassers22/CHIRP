from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

"""
SUMMARY:
This script captures video from a webcam (or other source), detects motion by comparing the difference 
between frames, and records a video when motion is detected AND a recording flag is set to True.
"""

class MotionDetector:
    """
    A class that captures video from a webcam (or other source), detects motion by comparing the difference 
    between frames, and records a video when motion is detected AND a recording flag is set to True.

    Attributes:
        FRAME_UPDATE_INTERVAL (int): Number of frames before updating the reference frame.
        MINIMUM_MOTION_AREA (int): Minimum contour area to be considered motion.
        MOTION_PERSISTENCE_DURATION (int): Number of frames to persist motion before stopping recording.
        video_capture (cv2.VideoCapture): Video capture object for the specified source.
        reference_frame (numpy.ndarray): Grayscale frame used as baseline for motion detection.
        motion_persistence_counter (int): Tracks frames remaining for motion persistence.
        frame_update_counter (int): Tracks frames until reference frame update.
        font_style (int): OpenCV font style for text overlay.
        video_writer (cv2.VideoWriter): Object for writing video to file, None if not recording.
        video_codec (int): FourCC code for video encoding (XVID).
        recording (bool): Flag to enable/disable video recording.
        announced_detected_motion (bool): Flag to track if motion detection has been announced.
    """

    # Class-level constants for motion detection sensitivity and persistence
    FRAME_UPDATE_INTERVAL = 10  # Number of frames before updating the reference frame
    MINIMUM_MOTION_AREA = 1000  # Minimum contour area to be considered motion
    MOTION_PERSISTENCE_DURATION = 50  # Number of frames to persist motion before stopping recording

    def __init__(self, stand=None):
        """
        Initialize the MotionDetector with a video source.
        Args:
            stand (optional): The rotating stand object, if present. Defaults to None.
        """
        # Ensure recordings directory exists, won't raise error if it already exists
        os.makedirs('./recordings', exist_ok=True)
        self.stand = stand
        
        # Initialize Picamera2 for capturing frames
        self.picam2 = Picamera2()
        config = self.picam2.create_still_configuration()
        config['size'] = (640, 480)  # Set resolution to 640x480
        self.picam2.configure(config)
        self.picam2.start()

        self.reference_frame = None  # Initial reference frame for motion detection
        self.motion_persistence_counter = 0  # Counter for motion persistence duration
        self.frame_update_counter = 0  # Counter for periodic reference frame updates
        self.font_style = cv2.FONT_HERSHEY_SIMPLEX  # Font for text overlay on video
        self.video_writer = None  # Video writer initialized when recording starts
        self.video_codec = cv2.VideoWriter_fourcc(*'XVID')  # XVID codec for video output
        self.recording = False  # Recording flag, toggled by user
        self.announced_detected_motion = False  # Tracks if motion detection was announced

    def process_frame(self, frame):
        """
        Process a raw video frame for motion detection and display/recording.
        """
        frame = cv2.flip(frame, 1)  # Flip horizontally to correct orientation
        frame_resized = cv2.resize(frame, (640, 480))  # Resize to standard width
        grayscale = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        blurred = cv2.GaussianBlur(grayscale, (21, 21), 0)  # Apply blur to reduce noise
        return blurred, frame_resized

    def detect_motion(self, reference_frame, current_frame):
        """
        Detect motion by analyzing differences between a reference frame and the current frame.
        """
        frame_difference = cv2.absdiff(reference_frame, current_frame)  # Calculate frame difference
        threshold_frame = cv2.threshold(frame_difference, 25, 255, cv2.THRESH_BINARY)[1]  # Binary threshold
        threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)  # Dilate to enhance motion regions
        contours, _ = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find contours
        return contours

    def run(self):
        """
        Run the main loop to capture video, detect motion, and record video when conditions are met.
        """
        try:
            while True:
                motion_detected = False  # Reset motion flag each frame
                frame = self.picam2.capture_array()  # Capture frame from Picamera2

                # Convert the captured frame from RGB to BGR
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                current_frame, processed_frame = self.process_frame(frame_bgr)  # Process the frame

                # Set initial reference frame if not yet defined
                if self.reference_frame is None:
                    self.reference_frame = current_frame

                # Update reference frame periodically
                self.frame_update_counter += 1
                if self.frame_update_counter > self.FRAME_UPDATE_INTERVAL:
                    self.frame_update_counter = 0
                    self.reference_frame = current_frame

                # Detect motion and draw bounding boxes
                motion_contours = self.detect_motion(self.reference_frame, current_frame)
                for contour in motion_contours:
                    if cv2.contourArea(contour) > self.MINIMUM_MOTION_AREA:  # Check if contour is significant
                        motion_detected = True
                        (x, y, width, height) = cv2.boundingRect(contour)  # Get bounding box coordinates
                        cv2.rectangle(processed_frame, (x, y), (x + width, y + height), (0, 255, 0), 2)  # Draw rectangle

                # Announce new motion detection
                if motion_detected and not self.announced_detected_motion:
                    self.announced_detected_motion = True
                    print("New Motion Detected")

                # Reset persistence counter on motion detection
                if motion_detected:
                    self.motion_persistence_counter = self.MOTION_PERSISTENCE_DURATION
                
                #Pause rotation when movement is detected
                if self.stand:
                    if self.motion_persistence_counter > 0:
                        self.stand.pause_rotation()  # Pause rotation when motion is detected
                    else:
                        self.stand.resume_rotation()  # Resume rotation when no motion is detected

                # Update status text based on motion and recording state
                if self.motion_persistence_counter > 0:
                    motion_status_text = f"Motion Detected ({self.motion_persistence_counter}) - Recording: {self.recording}"
                else:
                    motion_status_text = f"No Motion Detected - Recording: {self.recording}"
                
                if self.stand and self.stand.isRotating:
                    cv2.putText(processed_frame, "Rotating - Motion detection paused", (10, 70), self.font_style, 0.75, (0, 255, 255), 2, cv2.LINE_AA)


                # Decrease persistence counter, ensuring it doesn't go below 0
                self.motion_persistence_counter = max(0, self.motion_persistence_counter - 1)
                cv2.putText(processed_frame, motion_status_text, (10, 35), self.font_style, 0.75, (255, 255, 255), 2, cv2.LINE_AA)  # Overlay text
                cv2.imshow("Motion Detection", processed_frame)  # Display the frame

                # Initialize video writer if motion persists and recording is enabled
                if self.motion_persistence_counter > 0 and not self.video_writer and self.recording:
                    frame_height, frame_width, _ = frame.shape  # Get original frame dimensions
                    self.video_writer = cv2.VideoWriter(f'./recordings/{int(time.time())}_motion_video.avi', 
                                                      self.video_codec, 25.0, (frame_width, frame_height))

                # Write frame to video if recording
                if self.motion_persistence_counter > 0 and self.video_writer and self.recording:
                    self.video_writer.write(frame)

                # Stop recording when motion ceases
                if self.motion_persistence_counter == 0 and self.video_writer:
                    self.video_writer.release()
                    self.video_writer = None

                # Reset motion announcement flag when motion stops
                if self.motion_persistence_counter == 0:
                    self.announced_detected_motion = False

                # Handle user input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # Exit on 'q'
                    if self.video_writer:
                        self.video_writer.release()
                    break
                elif key == ord('r'):  # Toggle recording on 'r'
                    self.recording = not self.recording
                    print(f"Recording set to: {self.recording}")

        finally:
            # Clean up resources on exit
            print("Releasing video capture...")
            self.picam2.stop()
            if self.video_writer:
                print("Releasing video writer...")
                self.video_writer.release()
            print("Closing all windows...")
            cv2.destroyAllWindows()
            print("Cleanup complete.")

if __name__ == "__main__":
    """Entry point: Create a MotionDetector instance and run it."""
    detector = MotionDetector()  # Default source is camera
    detector.run()
