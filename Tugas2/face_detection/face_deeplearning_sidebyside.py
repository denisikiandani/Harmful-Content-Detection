import cv2
from mtcnn.mtcnn import MTCNN
import numpy as np

# Initialize the MTCNN face detector
detector = MTCNN()
video_capture = cv2.VideoCapture(0)

def resize_frame(frame, width):
    """Resize the frame to the given width while maintaining the aspect ratio."""
    aspect_ratio = frame.shape[1] / frame.shape[0]
    new_height = int(width / aspect_ratio)
    resized_frame = cv2.resize(frame, (width, new_height))
    return resized_frame

def detect_bounding_box_and_crop_faces(frame):
    """Detect faces in the frame, draw bounding boxes, and crop faces."""
    # Convert the frame to RGB (MTCNN expects RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_frame)
    cropped_faces = []
    for face in faces:
        x, y, w, h = face['box']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Crop and convert to grayscale
        cropped_face = frame[y:y+h, x:x+w]
        gray_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
        gray_face = cv2.cvtColor(gray_face, cv2.COLOR_GRAY2BGR) # Convert back to 3 channel
        cropped_faces.append(gray_face)
    return frame, cropped_faces

while True:
    result, video_frame = video_capture.read()
    if not result:
        break

    # Resize the frame to a width of 240 pixels
    video_frame = resize_frame(video_frame, 240)

    # Detect faces, draw bounding boxes, and get cropped faces
    processed_frame, cropped_faces = detect_bounding_box_and_crop_faces(video_frame)

    # Prepare a blank canvas to display both the original frame and cropped faces
    if len(cropped_faces) > 0:
        max_height = max(face.shape[0] for face in cropped_faces)
        total_width = sum(face.shape[1] for face in cropped_faces)

        # Height of the new canvas will be the max of original frame height and max_height of faces
        new_canvas_height = max(processed_frame.shape[0], max_height)
        new_canvas_width = processed_frame.shape[1] + total_width

        canvas = np.zeros((new_canvas_height, new_canvas_width, 3), dtype=np.uint8)

        # Place the processed frame on the left side of the canvas
        canvas[:processed_frame.shape[0], :processed_frame.shape[1]] = processed_frame

        # Place cropped faces on the right side of the canvas
        x_offset = processed_frame.shape[1]
        for face in cropped_faces:
            canvas[:face.shape[0], x_offset:x_offset + face.shape[1]] = face
            x_offset += face.shape[1]

        # Display the combined canvas
        cv2.imshow("Face Detection - Original and Cropped Faces", canvas)

    else:
        # If no faces are detected, just show the original processed frame
        cv2.imshow("Face Detection - Original and Cropped Faces", processed_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
