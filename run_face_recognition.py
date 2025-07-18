import cv2
import face_recognition
import numpy as np
import cvzone
from database_manager import DatabaseManager
from enhanced_encoder import EnhancedEncoder
import threading
import time

class FaceRecognitionSystem:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.encoder = EnhancedEncoder()
        self.encode_list_known = []
        self.models_ids = []
        self.load_encodings()
        self.access_granted = False
        self.access_message = ""
        self.last_recognition_time = 0
        self.recognition_cooldown = 2  # seconds
        
    def load_encodings(self):
        """Load face encodings from file"""
        encodings_data = self.encoder.load_encodings()
        if encodings_data:
            self.encode_list_known, self.models_ids = encodings_data
            print(f"Loaded {len(self.encode_list_known)} face encodings")
        else:
            print("No encodings loaded. Please generate encodings first.")
    
    def reload_encodings(self):
        """Reload encodings (useful after adding/removing people)"""
        self.load_encodings()
    
    def recognize_face(self, frame):
        """Recognize faces in the given frame"""
        current_time = time.time()
        
        # Resize frame for faster processing
        frame_s = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        frame_s = cv2.cvtColor(frame_s, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_current_frame = face_recognition.face_locations(frame_s)
        encode_current_frame = face_recognition.face_encodings(frame_s, face_current_frame)
        
        recognized_users = []
        
        for encode_face, face_loc in zip(encode_current_frame, face_current_frame):
            # Compare with known faces
            matches = face_recognition.compare_faces(self.encode_list_known, encode_face)
            face_distances = face_recognition.face_distance(self.encode_list_known, encode_face)
            
            # Find the best match
            if len(face_distances) > 0:
                match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[match_index]
                
                # Scale back face location coordinates
                top, right, bottom, left = face_loc
                top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
                
                # Draw rectangle around face
                if matches[match_index] and confidence > 0.6:  # Confidence threshold
                    user_id = self.models_ids[match_index]
                    user_info = self.db_manager.get_user(user_id)
                    
                    if user_info and user_info[6] == 'active':  # Check if user is active
                        # Draw green rectangle for recognized face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Add user name
                        cv2.putText(frame, user_info[2], (left, top - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        
                        recognized_users.append({
                            'user_id': user_id,
                            'name': user_info[2],
                            'confidence': confidence
                        })
                        
                        # Log access (with cooldown to prevent spam)
                        if current_time - self.last_recognition_time > self.recognition_cooldown:
                            self.db_manager.log_access(user_id, True)
                            self.last_recognition_time = current_time
                            print(f"Access granted for: {user_info[2]} (ID: {user_id})")
                    else:
                        # Draw red rectangle for inactive user
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                        cv2.putText(frame, "INACTIVE", (left, top - 10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                else:
                    # Draw red rectangle for unknown face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "UNKNOWN", (left, top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    
                    # Log failed access attempt
                    if current_time - self.last_recognition_time > self.recognition_cooldown:
                        self.db_manager.log_access("unknown", False)
                        self.last_recognition_time = current_time
                        print("Access denied for unknown face")
        
        return frame, recognized_users
    
    def start_camera_check(self, callback=None):
        """Start camera for face recognition checking"""
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera")
            return False

        print("Camera started. Press 'q' to quit, 'r' to reload encodings")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Perform face recognition
            frame, recognized_users = self.recognize_face(frame)

            # Add status text
            if recognized_users:
                status_text = f"ACCESS GRANTED - {len(recognized_users)} user(s) recognized"
                color = (0, 255, 0)
            else:
                status_text = "ACCESS DENIED - No authorized users detected"
                color = (0, 0, 255)

            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Add instructions
            cv2.putText(frame, "Press 'Q' to quit", (10, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Show frame
            cv2.imshow("Face Recognition System", frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("Reloading encodings...")
                self.reload_encodings()

            # Call callback if provided
            if callback:
                callback(recognized_users)

        cap.release()
        cv2.destroyAllWindows()
        return True
    def test_single_image(self, image_path):
        """Test recognition on a single image"""
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not read image"
        
        frame, recognized_users = self.recognize_face(img)
        
        cv2.imshow("Recognition Test", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True, recognized_users

if __name__ == "__main__":
    system = FaceRecognitionSystem()
    system.start_camera_check()