"""
Computer Vision Module
OCR, document understanding, image processing
"""

import logging
from typing import List, Dict, Tuple, Optional
import base64
from io import BytesIO
import numpy as np
from PIL import Image
import re

logger = logging.getLogger(__name__)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available. Install for OCR capabilities.")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not available. Install for advanced image processing.")


class OCRProcessor:
    """Optical Character Recognition for document images"""
    
    def __init__(self):
        self.available = TESSERACT_AVAILABLE
    
    def extract_text_from_image(self, image: np.ndarray) -> str:
        """Extract text from image using OCR"""
        if not self.available:
            logger.warning("Tesseract not available. Cannot perform OCR.")
            return ""
        
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    def extract_text_with_confidence(self, image: np.ndarray) -> List[Dict]:
        """Extract text with confidence scores"""
        if not self.available:
            return []
        
        try:
            data = pytesseract.image_to_data(Image.fromarray(image))
            results = []
            
            for line in data.split('\n')[1:]:  # Skip header
                parts = line.split('\t')
                if len(parts) >= 12:
                    text = parts[11]
                    confidence = float(parts[10])
                    if text.strip():
                        results.append({
                            'text': text,
                            'confidence': confidence,
                            'bbox': {
                                'left': int(parts[6]),
                                'top': int(parts[7]),
                                'width': int(parts[8]),
                                'height': int(parts[9])
                            }
                        })
            
            return results
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return []
    
    def extract_tables_from_image(self, image: np.ndarray) -> List[List[str]]:
        """Detect and extract table content from image"""
        if not OPENCV_AVAILABLE:
            return []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Find contours (potential table cells)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract text from detected regions
            table_data = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cell_image = image[y:y+h, x:x+w]
                text = self.extract_text_from_image(cell_image)
                if text.strip():
                    table_data.append(text)
            
            return [table_data] if table_data else []
        except Exception as e:
            logger.error(f"Table extraction error: {e}")
            return []


class ImageProcessor:
    """General image processing and enhancement"""
    
    def __init__(self):
        self.available = OPENCV_AVAILABLE
    
    def preprocess_document_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess document image for better OCR"""
        if not self.available:
            return image
        
        try:
            # Convert to grayscale if color
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply bilateral filter (preserves edges)
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Adaptive threshold
            processed = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            return processed
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image
    
    def detect_text_regions(self, image: np.ndarray) -> List[Dict]:
        """Detect regions containing text"""
        if not OPENCV_AVAILABLE:
            return []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Use morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            dilated = cv2.dilate(gray, kernel, iterations=3)
            
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 30 and h > 10:  # Filter small regions
                    regions.append({
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'area': w * h
                    })
            
            # Sort by area (largest first)
            regions.sort(key=lambda r: r['area'], reverse=True)
            return regions[:10]  # Return top 10
        except Exception as e:
            logger.error(f"Text region detection error: {e}")
            return []
    
    def detect_document_edges(self, image: np.ndarray) -> Optional[Tuple[float, float, float, float]]:
        """Detect document boundaries in image"""
        if not OPENCV_AVAILABLE:
            return None
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 100, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Largest contour is likely the document
                largest = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest)
                return (x, y, x + w, y + h)
            
            return None
        except Exception as e:
            logger.error(f"Edge detection error: {e}")
            return None
    
    def rotate_document(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate document image"""
        if not OPENCV_AVAILABLE:
            return image
        
        try:
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, matrix, (w, h))
            return rotated
        except Exception as e:
            logger.error(f"Rotation error: {e}")
            return image
    
    def deskew_document(self, image: np.ndarray) -> np.ndarray:
        """Automatically deskew a document image"""
        if not OPENCV_AVAILABLE:
            return image
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 50, 150)
            
            # Detect skew angle
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                angles = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if -45 < angle < 45:
                        angles.append(angle)
                
                if angles:
                    median_angle = np.median(angles)
                    return self.rotate_document(image, median_angle)
            
            return image
        except Exception as e:
            logger.error(f"Deskew error: {e}")
            return image


class DocumentAnalyzer:
    """Analyze document structure and layout"""
    
    def __init__(self):
        self.ocr = OCRProcessor()
        self.image_processor = ImageProcessor()
    
    def analyze_document_structure(self, image: np.ndarray) -> Dict:
        """Analyze overall document structure"""
        # Preprocess
        processed = self.image_processor.preprocess_document_image(image)
        
        # Detect text regions
        text_regions = self.image_processor.detect_text_regions(processed)
        
        # Detect edges
        edges = self.image_processor.detect_document_edges(processed)
        
        # Extract text
        extracted_text = self.ocr.extract_text_from_image(processed)
        
        return {
            'text_regions_count': len(text_regions),
            'text_regions': text_regions[:5],  # Top 5
            'document_edges': edges,
            'extracted_text': extracted_text,
            'text_density': self._calculate_text_density(text_regions, image.shape),
            'has_tables': len(self.ocr.extract_tables_from_image(processed)) > 0,
            'image_quality': self._estimate_image_quality(processed)
        }
    
    def _calculate_text_density(self, regions: List[Dict], image_shape: Tuple) -> float:
        """Calculate text density in document"""
        if not regions or not image_shape:
            return 0.0
        
        total_text_area = sum(r['area'] for r in regions)
        total_image_area = image_shape[0] * image_shape[1]
        
        return min(total_text_area / total_image_area, 1.0)
    
    def _estimate_image_quality(self, image: np.ndarray) -> str:
        """Estimate quality of document image"""
        if not OPENCV_AVAILABLE:
            return "unknown"
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Use Laplacian variance as quality metric
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if laplacian_var > 100:
                return "high"
            elif laplacian_var > 50:
                return "medium"
            else:
                return "low"
        except Exception as e:
            logger.error(f"Quality estimation error: {e}")
            return "unknown"


class ImageToBase64:
    """Convert between image and base64 formats"""
    
    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        """Convert numpy array image to base64 string"""
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image.astype('uint8'))
            
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            logger.error(f"Image to base64 conversion error: {e}")
            return ""
    
    @staticmethod
    def base64_to_image(img_str: str) -> Optional[np.ndarray]:
        """Convert base64 string to numpy array image"""
        try:
            img_data = base64.b64decode(img_str)
            image = Image.open(BytesIO(img_data))
            return np.array(image)
        except Exception as e:
            logger.error(f"Base64 to image conversion error: {e}")
            return None
