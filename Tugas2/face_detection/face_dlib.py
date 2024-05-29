import cv2
import dlib

# Initialize dlib's face detector (HOG-based)
detector = dlib.get_frontal_face_detector()

video_capture = cv2.VideoCapture(0)

def detect_bounding_box(vid):
    # Convert the frame to grayscale
    gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_image)
    for face in faces:
        x, y, w, h = (face.left(), face.top(), face.width(), face.height())
        cv2.rectangle(vid, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return faces

while True:
    result, video_frame = video_capture.read()
    if not result:
        break

    faces = detect_bounding_box(video_frame)

    cv2.imshow("My Face Detection Project", video_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
