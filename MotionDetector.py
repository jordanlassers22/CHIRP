import os
import sys
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0" 
os.environ["QT_QPA_PLATFORM"] = "offscreen"       

from picamera2 import Picamera2
import cv2
import numpy as np
import time
from alert_system import Alarm

HEADLESS = not os.environ.get("DISPLAY")


"""
SUMMARY:
This script captures video from a webcam (or other source), detects motion by comparing the difference 
between frames, and records a video when motion is detected AND a recording flag is set to True.
Reference Code: https://github.com/biplob004/Motion-detection-cv2
"""

class MotionDetector:
    """
    A class that detects motion using the PiCamera2 module, analyzes video frames for changes, and
    coordinates actions like pausing rotation, recording footage, and triggering alarms.

    Attributes:
        sentry (Sentry): Optional rotating base object to pause/resume based on detected motion.
        alarm (Alarm): Buzzer/alert component triggered on motion detection.
        reference_frame (np.ndarray): Grayscale frame used for motion comparison.
        motion_persistence_counter (int): Countdown timer to persist motion detection.
        frame_update_counter (int): Frame counter for updating the reference frame.
        font_style (int): OpenCV font style for display overlays.
        video_writer (cv2.VideoWriter): Optional writer for saving detected motion footage.
        video_codec (int): FOURCC encoding code (default: 'XVID').
        recording (bool): Toggle to enable/disable video recording.
        announced_detected_motion (bool): Internal flag to limit repeat alerts.
    """


    # Class-level constants for motion detection sensitivity and persistence
    FRAME_UPDATE_INTERVAL = 10  # Number of frames before updating the reference frame
    MINIMUM_MOTION_AREA = 3000  # Minimum contour area to be considered motion
    MOTION_PERSISTENCE_DURATION = 50  # Number of frames to persist motion before stopping recording
    

    def __init__(self, sentry=None):
        """
        Initialize the MotionDetector with a video source.
        Args:
            sentry (optional): The rotating sentry object, if present. Defaults to None.
        """
        # Ensure recordings directory exists, won't raise error if it already exists
        os.makedirs('./recordings', exist_ok=True)
        self.sentry = sentry
        self.alarm = Alarm()
        
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
        Prepare a video frame for motion analysis by flipping, resizing, grayscaling, and blurring.
        Args:
            frame (np.ndarray): Raw image from the camera in BGR format.
        Returns:
            Tuple[np.ndarray, np.ndarray]: Tuple of (processed grayscale frame, original resized frame).
        """
        frame = cv2.flip(frame, 1)  # Flip horizontally to correct orientation
        frame_resized = cv2.resize(frame, (640, 480))  # Resize to standard width
        grayscale = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        blurred = cv2.GaussianBlur(grayscale, (21, 21), 0)  # Apply blur to reduce noise
        return blurred, frame_resized

    def detect_motion(self, reference_frame, current_frame):
        """
        Compare the current frame with a reference to detect motion based on contour area.
        Args:
            reference_frame (np.ndarray): A grayscale baseline frame.
            current_frame (np.ndarray): The new grayscale frame to compare.
        Returns:
            List[np.ndarray]: A list of contours where significant movement was detected.
        """
        frame_difference = cv2.absdiff(reference_frame, current_frame)  # Calculate frame difference
        threshold_frame = cv2.threshold(frame_difference, 25, 255, cv2.THRESH_BINARY)[1]  # Binary threshold
        threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)  # Dilate to enhance motion regions
        contours, _ = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # Find contours
        return contours

    def run(self):
        """
        Continuously capture video frames and detect motion.
        - Detect movement using frame differencing.
        - Display and annotate the frame using OpenCV (unless in headless mode).
        - Pause/resume the sentry turret when motion is detected or ends.
        - Optionally record motion-triggered video clips to disk.
        - Monitor user input for quit ('q') or toggle recording ('r').
        - Ignore motion detection during turret rotation and wait 3s after rotation stops.
        """
        try:
            rotation_stopped_time = None  # Tracks when rotation stops
            POST_ROTATION_DELAY = 1.0  # Delay in seconds after rotation stops
            while True:
                motion_detected = False  # Reset motion flag each frame
                frame = self.picam2.capture_array()  # Capture frame from Picamera2

                # Convert the captured frame from RGB to BGR
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                current_frame, processed_frame = self.process_frame(frame_bgr)  # Process the frame

                # Set initial reference frame if not yet defined
                if self.reference_frame is None:
                    self.reference_frame = current_frame
                    #print("Initialized reference frame")

                # Skip motion detection if turret is rotating or in post-rotation delay
                if self.sentry and self.sentry.isRotating:
                    #print("Skipping motion detection: Turret is rotating")
                    # Reset motion state to avoid false positives
                    self.motion_persistence_counter = 0
                    self.announced_detected_motion = False
                    rotation_stopped_time = None  # Reset delay timer
                    self.reference_frame = current_frame  # Update reference frame to current
                else:
                    # Check if rotation recently stopped
                    if self.sentry and rotation_stopped_time is None and not self.sentry.isRotating:
                        #print("Rotation stopped, starting 3s delay")
                        rotation_stopped_time = time.time()
                        self.reference_frame = current_frame  # Reset reference frame
                        self.motion_persistence_counter = 0  # Clear any prior motion
                        self.announced_detected_motion = False

                    # Only process motion if not in post-rotation delay
                    if (rotation_stopped_time is None or time.time() - rotation_stopped_time >= POST_ROTATION_DELAY):
                        if rotation_stopped_time is not None and time.time() - rotation_stopped_time < POST_ROTATION_DELAY + 0.1:
                            self.reference_frame = current_frame
                            #print("Reset reference frame after post-rotation delay")

                        # Update reference frame periodically, but only if not in delay
                        self.frame_update_counter += 1
                        if self.frame_update_counter > self.FRAME_UPDATE_INTERVAL:
                            self.frame_update_counter = 0
                            self.reference_frame = current_frame
                            #print("Updated reference frame")

                        # Detect motion and draw bounding boxes
                        motion_contours = self.detect_motion(self.reference_frame, current_frame)
                        for contour in motion_contours:
                            area = cv2.contourArea(contour)
                            if area > self.MINIMUM_MOTION_AREA:  # Check if contour is significant
                                motion_detected = True
                                print(f"Motion detected with contour area: {area}")
                                (x, y, width, height) = cv2.boundingRect(contour)  # Get bounding box coordinates
                                cv2.rectangle(processed_frame, (x, y), (x + width, y + height), (0, 255, 0), 2)  # Draw rectangle

                        # Announce new motion detection
                        if motion_detected and not self.announced_detected_motion:
                            self.announced_detected_motion = True
                            print("New Motion Detected (actual motion)")
                            # self.alarm.sound_for(duration=2, repeats=1)

                        # Reset persistence counter on motion detection
                        if motion_detected:
                            self.motion_persistence_counter = self.MOTION_PERSISTENCE_DURATION

                    #else:
                        #print(f"Skipping motion detection: In post-rotation delay ({time.time() - rotation_stopped_time:.2f}s remaining)")

                # Pause rotation when movement is detected (only if not rotating)
                if self.sentry:
                    if (self.motion_persistence_counter > 0 and 
                        not self.sentry._pause_event.is_set() and 
                        not self.sentry.isRotating):
                        self.sentry.pause_rotation()
                    elif (self.motion_persistence_counter == 0 and 
                          self.sentry._pause_event.is_set()):
                        self.sentry.resume_rotation()

                # Decrease persistence counter, ensuring it doesn't go below 0
                self.motion_persistence_counter = max(0, self.motion_persistence_counter - 1)

                if not HEADLESS:
                    # Update status text based on motion and recording state
                    if self.sentry and self.sentry.isRotating:
                        motion_status_text = "Rotating - Motion detection paused"
                    elif rotation_stopped_time and time.time() - rotation_stopped_time < POST_ROTATION_DELAY:
                        motion_status_text = f"Post-rotation delay - Motion detection paused"
                    elif self.motion_persistence_counter > 0:
                        motion_status_text = f"Motion Detected ({self.motion_persistence_counter}) - Recording: {self.recording}"
                    else:
                        motion_status_text = f"No Motion Detected - Recording: {self.recording}"

                    cv2.putText(processed_frame, motion_status_text, (10, 35), self.font_style, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

                    if self.sentry and self.sentry.isRotating:
                        cv2.putText(processed_frame, "Rotating - Motion detection paused", (10, 70), self.font_style, 0.75, (0, 255, 255), 2, cv2.LINE_AA)

                    cv2.imshow("Motion Detection", processed_frame)

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
                if not HEADLESS:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        if self.video_writer:
                            self.video_writer.release()
                        break
                    elif key == ord('r'):
                        self.recording = not self.recording
                        print(f"Recording set to: {self.recording}")
                else:
                    time.sleep(0.05)  # Prevent 100% CPU usage

        finally:
            print("Releasing video capture...")
            self.picam2.stop()

            if self.video_writer:
                print("Releasing video writer...")
                self.video_writer.release()
                self.video_writer = None

            if not HEADLESS:
                print("Closing all windows...")
                cv2.destroyAllWindows()

            print("Cleanup complete.")


if __name__ == "__main__":
    """Entry point: Create a MotionDetector instance and run it."""
    detector = MotionDetector()  # Default source is camera
    detector.run()
