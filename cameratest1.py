import cv2

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Using V4L2 for Raspberry Pi with libcamera
if not cap.isOpened():
    print("Error: Camera not found or not accessible.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
