import cv2
import numpy as np
import face_recognition
import pickle
import os
from django.conf import settings
from django.core.files.base import ContentFile
import base64
from datetime import datetime
import logging

from face_app.models import FaceImage

logger = logging.getLogger(__name__)

class FaceRecognitionSystem:
    def __init__(self):
        self.tolerance = settings.FACE_RECOGNITION_SETTINGS.get('TOLERANCE', 0.6)
        self.model = settings.FACE_RECOGNITION_SETTINGS.get('MODEL', 'hog')
        self.num_jitters = settings.FACE_RECOGNITION_SETTINGS.get('NUM_JITTERS', 1)
        self.face_image_size = settings.FACE_RECOGNITION_SETTINGS.get('FACE_IMAGE_SIZE', (500, 500))
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known face encodings from database"""
        from users.models import CustomUser
        
        try:
            registered_users = CustomUser.objects.filter(is_face_registered=True).exclude(face_encoding=None)
            
            for user in registered_users:
                if user.face_encoding:
                    try:
                        # Decode face encoding from binary
                        encoding = pickle.loads(user.face_encoding)
                        self.known_face_encodings.append(encoding)
                        self.known_face_names.append(user.username)
                        self.known_face_ids.append(user.id)
                    except Exception as e:
                        logger.error(f"Error loading face encoding for user {user.username}: {e}")
            
            logger.info(f"Loaded {len(self.known_face_encodings)} known faces from database")
        except Exception as e:
            logger.error(f"Error loading known faces: {e}")
    
    def encode_face(self, image_path=None, image_array=None):
        """
        Encode a face from image path or numpy array
        
        Args:
            image_path: Path to image file
            image_array: Numpy array of image
            
        Returns:
            face_encoding or None
        """
        try:
            # Load image
            if image_path:
                image = face_recognition.load_image_file(image_path)
            elif image_array is not None:
                image = image_array
            else:
                logger.error("No image provided for encoding")
                return None
            
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 1:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(
                image, 
                model=self.model
            )
            
            if not face_locations:
                logger.warning("No face found in image")
                return None
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(
                image, 
                face_locations,
                num_jitters=self.num_jitters
            )
            
            if not face_encodings:
                logger.warning("Could not encode face")
                return None
            
            return face_encodings[0]  # Return first face encoding
            
        except Exception as e:
            logger.error(f"Error encoding face: {e}")
            return None
    
    def register_face(self, user, images):

        encodings = []

        for img in images:

            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            faces = face_recognition.face_locations(rgb)

            if len(faces) == 0:
                continue

            encoding = face_recognition.face_encodings(rgb, faces)[0]

            encodings.append(encoding)

            FaceImage.objects.create(
                person_id=user.id,
                encoding=encoding.tolist()
            )

        if len(encodings) > 0:
            user.is_face_registered = True
            user.save()
            return True

        return False
    
    def recognize_face(self, image, tolerance=None):
        """
        Recognize a face from image
        
        Args:
            image: Numpy array of image
            tolerance: Matching tolerance
            
        Returns:
            dict with user info or None
        """
        try:
            if tolerance is None:
                tolerance = self.tolerance
            
            # Encode the face in the image
            face_encoding = self.encode_face(image_array=image)
            
            if face_encoding is None:
                return None
            
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding, 
                tolerance=tolerance
            )
            
            # Find the best match
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encoding
            )
            
            if not matches or not any(matches):
                logger.info("No match found")
                return None
            
            # Get the index of the best match
            best_match_index = np.argmin(face_distances)
            
            if not matches[best_match_index]:
                logger.info("Best match below threshold")
                return None
            
            confidence = 1 - face_distances[best_match_index]
            
            # Return user info
            from users.models import CustomUser
            user = CustomUser.objects.get(id=self.known_face_ids[best_match_index])
            
            return {
                'user_id': user.id,
                'username': user.username,
                'name': user.get_full_name(),
                'confidence': round(confidence * 100, 2),
                'student_id': user.student_id,
                'match_index': best_match_index
            }
            
        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return None
    
    def detect_faces(self, image):
        """
        Detect all faces in image
        
        Returns:
            List of face locations and encodings
        """
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(
                image, 
                model=self.model
            )
            
            if not face_locations:
                return []
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(
                image, 
                face_locations,
                num_jitters=self.num_jitters
            )
            
            return list(zip(face_locations, face_encodings))
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def draw_faces(self, image, face_data_list):
        """
        Draw rectangles and labels on faces
        
        Args:
            image: Original image
            face_data_list: List of (location, encoding, name) tuples
            
        Returns:
            Image with drawings
        """
        try:
            # Convert to BGR for OpenCV if in RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            for face_data in face_data_list:
                if len(face_data) >= 3:
                    top, right, bottom, left = face_data[0]
                    name = face_data[2]
                    confidence = face_data[3] if len(face_data) > 3 else None
                    
                    # Draw rectangle
                    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                    
                    # Draw label background
                    cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                    
                    # Draw name
                    font = cv2.FONT_HERSHEY_DUPLEX
                    label = f"{name}"
                    if confidence:
                        label += f" ({confidence}%)"
                    cv2.putText(image, label, (left + 6, bottom - 6), font, 0.5, (0, 0, 0), 1)
            
            return image
            
        except Exception as e:
            logger.error(f"Error drawing faces: {e}")
            return image

    def image_to_base64(self, image):
        """Convert OpenCV image to base64 string"""
        try:
            # Convert BGR to RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{image_base64}"
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None

# Singleton instance
face_system = FaceRecognitionSystem()