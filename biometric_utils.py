import cv2
import numpy as np
import os

MODELS_DIR = "models"
prototxt_path = os.path.join(MODELS_DIR, "deploy.prototxt")
caffe_model_path = os.path.join(MODELS_DIR, "res10_300x300_ssd_iter_140000.caffemodel")
embedder_path = os.path.join(MODELS_DIR, "openface_nn4.small2.v1.t7") # Updated to match downloaded file name

# Load models if they exist
try:
    detector = cv2.dnn.readNetFromCaffe(prototxt_path, caffe_model_path)
    embedder = cv2.dnn.readNetFromTorch(embedder_path)
except Exception as e:
    print(f"Warning: Models not loaded. Please run download_models.py first. Error: {e}")
    detector = None
    embedder = None

def capture_face(window_name="Face Capture"):
    """
    Opens the default camera, shows a preview, and waits for the user to press 'SPACE' to capture.
    Returns the captured image frame (numpy array) or None if cancelled.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    captured_frame = None
    print(f"\n--- {window_name} ---")
    print("Look at the camera and press 'SPACE' to capture.")
    print("Press 'ESC' or 'Q' to cancel.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Mirror the frame vertically for intuitive viewing
        display_frame = cv2.flip(frame, 1)
        
        # Draw a simple guide box in the center
        height, width = display_frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        box_size = 200
        
        # Add visual guide
        cv2.rectangle(
            display_frame, 
            (center_x - box_size, center_y - box_size), 
            (center_x + box_size, center_y + box_size), 
            (0, 255, 0), 2
        )
        cv2.putText(display_frame, "Align face here & press SPACE", (center_x - box_size, center_y - box_size - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow(window_name, display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE bar
            # Capture the original, un-mirrored frame
            captured_frame = frame
            break
        elif key == 27 or key == ord('q'):  # ESC or Q
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_frame

def get_face_embedding(img_frame):
    """
    Extracts the facial embedding vector from an image frame using OpenCV DNN openface.
    Returns a list of floats (128-D embedding) or None if no face is detected/error.
    """
    if detector is None or embedder is None:
        print("Error: Models are not loaded.")
        return None

    (h, w) = img_frame.shape[:2]
    image_blob = cv2.dnn.blobFromImage(
        cv2.resize(img_frame, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0), swapRB=False, crop=False)

    detector.setInput(image_blob)
    detections = detector.forward()

    if len(detections) > 0:
        # Find the detection with largest probability
        i = np.argmax(detections[0, 0, :, 2])
        confidence = detections[0, 0, i, 2]

        if confidence > 0.5:
            # Extract bounding box
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Ensure bounding box is within dimensions
            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(w, endX)
            endY = min(h, endY)

            # Extract face ROI
            face = img_frame[startY:endY, startX:endX]
            if face.shape[0] < 20 or face.shape[1] < 20: 
                return None # Face too small

            # Process face through embedder model (OpenFace requires 96x96)
            face_blob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                (96, 96), (0, 0, 0), swapRB=True, crop=False)
            
            embedder.setInput(face_blob)
            vec = embedder.forward()

            return vec.flatten().tolist()
    return None

def verify_embedding_distance(embedding1, embedding2, threshold=0.7):
    """
    Calculates distance between two OpenFace 128-d embeddings.
    For OpenFace, typical threshold is between 0.6 and 0.8.
    Returns (match_boolean, distance_score).
    """
    if embedding1 is None or embedding2 is None:
        return False, None
        
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Euclidean distance
    distance = float(np.linalg.norm(vec1 - vec2))
    print(f"[Debug] Euclidean distance: {distance:.4f} (Threshold: {threshold})")
    
    return distance <= threshold, distance
