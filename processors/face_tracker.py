import numpy as np
from collections import deque

class FaceTracker:
    def __init__(self, max_distance=50, max_frames_to_skip=30):
        self.tracked_faces = {}
        self.next_id = 0
        self.max_distance = max_distance
        self.max_frames_to_skip = max_frames_to_skip
    
    def update(self, detections):
        """
        Update tracker with new detections
        Returns: dictionary of {face_id: bbox}
        """
        if len(detections) == 0:
            return self.tracked_faces
        
        # Match detections with existing tracks
        matched_faces = {}
        used_detections = set()
        
        for face_id, face_data in self.tracked_faces.items():
            min_distance = float('inf')
            best_detection_idx = -1
            
            for idx, detection in enumerate(detections):
                if idx in used_detections:
                    continue
                
                distance = self._calculate_distance(face_data['bbox'], detection['bbox'])
                
                if distance < min_distance and distance < self.max_distance:
                    min_distance = distance
                    best_detection_idx = idx
            
            if best_detection_idx != -1:
                matched_faces[face_id] = {
                    'bbox': detections[best_detection_idx]['bbox'],
                    'frames_without_detection': 0
                }
                used_detections.add(best_detection_idx)
            else:
                face_data['frames_without_detection'] += 1
                if face_data['frames_without_detection'] < self.max_frames_to_skip:
                    matched_faces[face_id] = face_data
        
        # Add new faces
        for idx, detection in enumerate(detections):
            if idx not in used_detections:
                matched_faces[self.next_id] = {
                    'bbox': detection['bbox'],
                    'frames_without_detection': 0
                }
                self.next_id += 1
        
        self.tracked_faces = matched_faces
        return matched_faces
    
    def _calculate_distance(self, bbox1, bbox2):
        """Calculate distance between two bounding boxes"""
        x1_center = (bbox1[0] + bbox1[2]) / 2
        y1_center = (bbox1[1] + bbox1[3]) / 2
        
        x2_center = (bbox2[0] + bbox2[2]) / 2
        y2_center = (bbox2[1] + bbox2[3]) / 2
        
        distance = np.sqrt((x1_center - x2_center)**2 + (y1_center - y2_center)**2)
        return distance