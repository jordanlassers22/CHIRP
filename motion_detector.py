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

    Reference Code: https://github.com/biplob004/Motion-detection-cv2
    """

    #Class-level constants for motion detection sensitivity and persistence
    FRAME_UPDATE_INTERVAL = 10  #Number of frames before updating the reference frame
    MINIMUM_MOTION_AREA = 4000  #Minimum contour area to be considered motion
    MOTION_PERSISTENCE_DURATION = 100  #Number of frames to persist motion before stopping recording

    def __init__(self, source=0, stand=None):
        """
        Initialize the MotionDetector with a video source.

        Args:
            source (int or str, optional): Video source (e.g., 0 for default webcam, or a file path). Defaults to 0.
        """
        #Ensure recordings directory exists, won't raise error if it already exists
        os.makedirs('./recordings', exist_ok=True)
        self.stand = stand
        self.video_capture = self.initialize_video_capture(source)  #Set up video capture
        self.reference_frame = None  #Initial reference frame for motion detection
        self.motion_persistence_counter = 0  #Counter for motion persistence duration
        self.frame_update_counter = 0  #Counter for periodic reference frame updates
        self.font_style = cv2.FONT_HERSHEY_SIMPLEX  #Font for text overlay on video
        self.video_writer = None  #Video writer initialized when recording starts
        self.video_codec = cv2.VideoWriter_fourcc(*'XVID')  #XVID codec for video output
        self.recording = False  #Recording flag, toggled by user
        self.announced_detected_motion = False  #Tracks if motion detection was announced

    def initialize_video_capture(self, source):
        """
        Initialize video capture from the given source.

        Args:
            source (int or str): Video source (e.g., 0 for webcam, or a file path).

        Returns:
            cv2.VideoCapture: Initialized video capture object.
        """
        return cv2.VideoCapture(source)

    def process_frame(self, frame):
        """
        Process a raw video frame for motion detection and display/recording.

        This function flips the frame horizontally, resizes it, and prepares two versions: a grayscale
        blurred version for motion detection and a color resized version for display and recording.

        Args:
            frame (numpy.ndarray): Raw input frame in BGR color format (3 channels).

        Returns:
            tuple: (blurred, frame_resized)
                - blurred (numpy.ndarray): Grayscale, blurred frame for motion detection.
                - frame_resized (numpy.ndarray): Resized, flipped color frame for display/recording.
        """
        frame = cv2.flip(frame, 1)  #Flip horizontally to correct orientation
        frame_resized = imutils.resize(frame, width=750)  #Resize to standard width
        grayscale = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  #Convert to grayscale
        blurred = cv2.GaussianBlur(grayscale, (21, 21), 0)  #Apply blur to reduce noise
        return blurred, frame_resized

    def detect_motion(self, reference_frame, current_frame):
        """
        Detect motion by analyzing differences between a reference frame and the current frame.

        Computes the absolute difference, applies a binary threshold, dilates the result, and finds contours.

        Args:
            reference_frame (numpy.ndarray): Grayscale reference frame for baseline comparison.
            current_frame (numpy.ndarray): Grayscale current frame to compare against reference.

        Returns:
            list: Contours (numpy.ndarray) representing regions of detected motion.
        """
        frame_difference = cv2.absdiff(reference_frame, current_frame)  #Calculate frame difference
        threshold_frame = cv2.threshold(frame_difference, 25, 255, cv2.THRESH_BINARY)[1]  #Binary threshold
        threshold_frame = cv2.dilate(threshold_frame, None, iterations=2)  #Dilate to enhance motion regions
        contours, _ = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  #Find contours
        return contours

    def run(self):
        """
        Run the main loop to capture video, detect motion, and record video when conditions are met.

        This method processes frames, detects motion, annotates the video feed, and records when motion
        persists and recording is enabled. It exits on 'q' keypress and toggles recording with 'r'.

        Key Controls:
            'q': Quit the loop and clean up resources.
            'r': Toggle recording on/off.
        """
        try:
            while True:
                motion_detected = False  #Reset motion flag each frame
                ret, frame = self.video_capture.read()  #Read frame from video source
                if not ret:
                    print("CAPTURE ERROR: Could not read frame")
                    continue

                 # Skip processing while rotating
                if self.stand and self.stand.isRotating:
                    print("Skipping motion detection — camera is rotating")
                    _, frame_resized = self.process_frame(frame)
                    cv2.putText(frame_resized, "Rotating - Motion Detection Paused", (10, 35), self.font_style, 0.75, (0, 255, 255), 2, cv2.LINE_AA)
                    cv2.imshow("Motion Detection", frame_resized)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        if self.video_writer:
                            self.video_writer.release()
                        break
                    elif key == ord('r'):
                        self.recording = not self.recording
                        print(f"Recording set to: {self.recording}")
                    continue
                
                current_frame, processed_frame = self.process_frame(frame)  #Process the frame

                #Set initial reference frame if not yet defined
                if self.reference_frame is None:
                    self.reference_frame = current_frame

                #Update reference frame periodically
                self.frame_update_counter += 1
                if self.frame_update_counter > self.FRAME_UPDATE_INTERVAL:
                    self.frame_update_counter = 0
                    self.reference_frame = current_frame

                #Detect motion and draw bounding boxes
                motion_contours = self.detect_motion(self.reference_frame, current_frame)
                for contour in motion_contours:
                    if cv2.contourArea(contour) > self.MINIMUM_MOTION_AREA:  #Check if contour is significant
                        motion_detected = True
                        (x, y, width, height) = cv2.boundingRect(contour)  #Get bounding box coordinates
                        cv2.rectangle(processed_frame, (x, y), (x + width, y + height), (0, 255, 0), 2)  #Draw rectangle

                #Announce new motion detection
                if motion_detected and not self.announced_detected_motion:
                    self.announced_detected_motion = True
                    print("New Motion Detected")

                #Reset persistence counter on motion detection
                if motion_detected:
                    self.motion_persistence_counter = self.MOTION_PERSISTENCE_DURATION
                    
                # Pause or resume rotating stand based on motion
                if self.stand:
                    if self.motion_persistence_counter > 0:
                        self.stand.pause_rotation()
                    else:
                        self.stand.resume_rotation()


                #Update status text based on motion and recording state
                if self.motion_persistence_counter > 0:
                    motion_status_text = f"Motion Detected ({self.motion_persistence_counter}) - Recording: {self.recording}"
                else:
                    motion_status_text = f"No Motion Detected - Recording: {self.recording}"

                #Decrease persistence counter, ensuring it doesn't go below 0
                self.motion_persistence_counter = max(0, self.motion_persistence_counter - 1)
                cv2.putText(processed_frame, motion_status_text, (10, 35), self.font_style, 0.75, (255, 255, 255), 2, cv2.LINE_AA)  #Overlay text
                cv2.imshow("Motion Detection", processed_frame)  #Display the frame

                #Initialize video writer if motion persists and recording is enabled
                if self.motion_persistence_counter > 0 and not self.video_writer and self.recording:
                    frame_height, frame_width, _ = frame.shape  #Get original frame dimensions
                    self.video_writer = cv2.VideoWriter(f'./recordings/{int(time.time())}_motion_video.avi', 
                                                      self.video_codec, 25.0, (frame_width, frame_height))

                #Write frame to video if recording
                if self.motion_persistence_counter > 0 and self.video_writer and self.recording:
                    self.video_writer.write(frame)

                #Stop recording when motion ceases
                if self.motion_persistence_counter == 0 and self.video_writer:
                    self.video_writer.release()
                    self.video_writer = None

                #Reset motion announcement flag when motion stops
                if self.motion_persistence_counter == 0:
                    self.announced_detected_motion = False

                #Handle user input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  #Exit on 'q'
                    if self.video_writer:
                        self.video_writer.release()
                    break
                elif key == ord('r'):  #Toggle recording on 'r'
                    self.recording = not self.recording
                    print(f"Recording set to: {self.recording}")

        finally:
            #Clean up resources on exit
            print("Releasing video capture...")
            self.video_capture.release()
            if self.video_writer:
                print("Releasing video writer...")
                self.video_writer.release()
            print("Closing all windows...")
            cv2.destroyAllWindows()
            print("Cleanup complete.")

if __name__ == "__main__":
    """Entry point: Create a MotionDetector instance and run it."""
    detector = MotionDetector()  #Default source is webcam (0)
    detector.run()