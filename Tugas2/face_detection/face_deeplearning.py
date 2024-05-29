import cv2
from mtcnn.mtcnn import MTCNN

# Initialize the MTCNN face detector
detector = MTCNN()
video_capture = cv2.VideoCapture(0)

def resize_frame(frame, width):
    """Resize the frame to the given width while maintaining the aspect ratio."""
    aspect_ratio = frame.shape[1] / frame.shape[0]
    new_height = int(width / aspect_ratio)
    resized_frame = cv2.resize(frame, (width, new_height))
    return resized_frame

def detect_bounding_box(frame):
    """Detect faces in the frame and draw bounding boxes around them."""
    # Convert the frame to RGB (MTCNN expects RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_frame)
    for face in faces:
        x, y, w, h = face['box']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return faces

while True:
    result, video_frame = video_capture.read()
    if not result:
        break

    # Resize the frame to a width of 192 pixels
    video_frame = resize_frame(video_frame, 192)

    # Detect faces and draw bounding boxes
    faces = detect_bounding_box(video_frame)

    # Display the processed frame
    cv2.imshow("My Face Detection Project", video_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
