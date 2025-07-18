import os
import cv2
import face_recognition
import pickle
from database_manager import DatabaseManager

class EnhancedEncoder:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.encodings_file = "EncodedImages.p"
    
    def generate_encoded_images(self):
        """Generate encodings for all images in the img/Modes folder"""
        folder_path = 'img/Modes'
        
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' does not exist!")
            return False
        
        path_list = os.listdir(folder_path)
        if not path_list:
            print(f"Error: No images found in '{folder_path}'!")
            return False
        
        img_list = []
        models_ids = []
        
        print("Loading images...")
        for path in path_list:
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(folder_path, path)
                img = cv2.imread(img_path)
                if img is not None:
                    img_list.append(img)
                    models_ids.append(os.path.splitext(path)[0])
                    print(f"Loaded: {path}")
        
        if not img_list:
            print("Error: No valid images found!")
            return False
        
        print("Encoding started...")
        encode_list_known = self.find_encodings(img_list)
        
        if not encode_list_known:
            print("Error: No faces found in images!")
            return False
        
        encode_list_known_with_ids = [encode_list_known, models_ids]
        print("Encoding finished")
        
        # Save encodings to file
        with open(self.encodings_file, 'wb') as file:
            pickle.dump(encode_list_known_with_ids, file)
        
        print(f"Encodings saved to {self.encodings_file}")
        return True
    
    def find_encodings(self, images_list):
        """Find face encodings for a list of images"""
        encode_list = []
        
        for i, img in enumerate(images_list):
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Find face locations first
            face_locations = face_recognition.face_locations(img_rgb)
            
            if face_locations:
                # Get encodings for detected faces
                face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
                if face_encodings:
                    encode_list.append(face_encodings[0])  # Take the first face
                    print(f"Face encoded for image {i+1}")
                else:
                    print(f"Warning: No face encoding found for image {i+1}")
            else:
                print(f"Warning: No face detected in image {i+1}")
        
        return encode_list
    
    def add_new_person(self, image_path, user_id, name, email="", phone="", department=""):
        """Add a new person to the system"""
        try:
            # Read and process the image
            img = cv2.imread(image_path)
            if img is None:
                return False, "Could not read image file"
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img_rgb)
            
            if not face_locations:
                return False, "No face detected in the image"
            
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            if not face_encodings:
                return False, "Could not encode face"
            
            # Save image to modes folder
            modes_folder = 'img/Modes'
            if not os.path.exists(modes_folder):
                os.makedirs(modes_folder)
            
            # Save image with user_id as filename
            img_filename = f"{user_id}.jpg"
            img_save_path = os.path.join(modes_folder, img_filename)
            cv2.imwrite(img_save_path, img)
            
            # Add user to database
            if self.db_manager.add_user(user_id, name, email, phone, department):
                # Regenerate encodings
                self.generate_encoded_images()
                return True, "Person added successfully"
            else:
                # Remove image if database insertion failed
                if os.path.exists(img_save_path):
                    os.remove(img_save_path)
                return False, "User ID already exists"
            
        except Exception as e:
            return False, f"Error adding person: {str(e)}"
    
    def remove_person(self, user_id):
        """Remove a person from the system"""
        try:
            # Remove from database
            self.db_manager.delete_user(user_id)
            
            # Remove image file
            img_path = os.path.join('img/Modes', f"{user_id}.jpg")
            if os.path.exists(img_path):
                os.remove(img_path)
            
            # Regenerate encodings
            self.generate_encoded_images()
            return True, "Person removed successfully"
        
        except Exception as e:
            return False, f"Error removing person: {str(e)}"
    
    def load_encodings(self):
        """Load encodings from file"""
        try:
            with open(self.encodings_file, 'rb') as file:
                encode_list_known_with_ids = pickle.load(file)
            return encode_list_known_with_ids
        except FileNotFoundError:
            print("Encodings file not found. Please generate encodings first.")
            return None
        except Exception as e:
            print(f"Error loading encodings: {str(e)}")
            return None

if __name__ == "__main__":
    encoder = EnhancedEncoder()
    encoder.generate_encoded_images()