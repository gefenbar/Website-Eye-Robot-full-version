import pytesseract
import cv2
import numpy as np
import re
# for testing
# import os

def detect_small_text(img_path, save_path):
    img = load_image(img_path)
    # cv2.imwrite("original_image_small_text.jpg", img)
    height, width = img.shape[:2]
    min_height, max_height = calculate_min_max_height(height)
    gray = preprocess_image(img)
    # cv2.imwrite("grayscale_image_small_text.jpg", gray)

    denoised = denoise_image(gray)
    # cv2.imwrite("denoised_image_small_text.jpg", denoised)

    thresh = threshold_image(denoised)
    # cv2.imwrite("thresholded_image_small_text.jpg", thresh)

    thresh = apply_morphological_operations(thresh)
    # cv2.imwrite("morphological_operations_small_text.jpg", thresh)

    contours = find_contours(thresh)

    img_copy = img.copy()
    found_issue = False

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if min_height <= h <= max_height and is_full_text_contour(contour, width, height):
            # Exclude cropped text
            if is_cropped_text(contour, width, height):
                continue

            # Remove a small portion from top and bottom
            top_margin = int(h * 0.1)
            bottom_margin = int(h * 0.1)
            y += top_margin
            h -= (top_margin + bottom_margin)

            crop_img = img[y:y+h, x:x+w]

            # Zoom in on small text
            zoomed_img = zoom_in(crop_img, zoom_factor=5)

            if contains_text(zoomed_img):
                found_issue = True
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (15, 15, 245), 2)

    if found_issue:
        print("Found SMALL_TEXT issue")
        cv2.imwrite(save_path, img_copy)
        return save_path
    else:
        print("Not found SMALL_TEXT issue")
        return ""


def load_image(img_path):
    return cv2.imread(img_path)


def calculate_min_max_height(height):
    reference_height = height
    min_height = 2
    max_height = 7
    ratio = height / reference_height
    min_height = int(ratio * min_height)
    max_height = int(ratio * max_height)
    return min_height, max_height


def preprocess_image(img):
    # Apply denoising before converting to grayscale
    denoised = cv2.bilateralFilter(img, 9, 75, 75)
    gray = cv2.cvtColor(denoised, cv2.COLOR_BGR2GRAY)
    return gray


def denoise_image(gray):
    # Apply additional denoising if needed
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    return denoised


def threshold_image(gray):
    # Experiment with different thresholding methods
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh


def apply_morphological_operations(thresh):
    kernel_size = 1
    kernel_shape = cv2.MORPH_ELLIPSE
    kernel = cv2.getStructuringElement(
        kernel_shape, (kernel_size, kernel_size))

    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return thresh


def find_contours(thresh):
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def is_full_text_contour(contour, image_width, image_height):
    # Check if contour is likely to contain full text
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / float(h)
    if aspect_ratio > 0.1 and aspect_ratio < 0.9 and y > 0.1 * image_height:
        return True
    return False


def is_cropped_text(contour, image_width, image_height):
    # Check if contour is too close to the image boundaries, indicating cropped text
    x, y, w, h = cv2.boundingRect(contour)
    boundary_threshold = 0.3
    if x < boundary_threshold * image_width or (x + w) > (1 - boundary_threshold) * image_width:
        return True
    return False


def contains_text(crop_img):
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6 --oem 1')
    
    # Exclude specific characters or symbols
    excluded_characters = excluded_characters = [',', '.', "'", 'o', '•', '·', '⋅', 'o']  

    # Check if the detected text contains any excluded characters
    for char in excluded_characters:
        if char in text:
            return False
        
    return re.search(r'\w', text)



def zoom_in(img, zoom_factor):
    zoomed_img = cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)
    return zoomed_img



# def test_directory(directory_path, save_directory):
#     # Create the save directory if it doesn't exist
#     if not os.path.exists(save_directory):
#         os.makedirs(save_directory)

#     # Iterate over all files in the directory
#     for filename in os.listdir(directory_path):
#         if filename.endswith(".png") or filename.endswith(".jpg"):
#             # Construct the full paths for the input image and save path
#             img_path = os.path.join(directory_path, filename)
#             save_path = os.path.join(save_directory, filename)

#             # Call the detect_small_text function
#             result = detect_small_text(img_path, save_path)
#             if result:
#                 print(f"SMALL_TEXT issue detected in {img_path}. Annotated image saved as {result}.")
#             else:
#                 print(f"No SMALL_TEXT issue found in {img_path}.")

# Test the directory
# directory_path = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/NO_ISSUES/"
# save_directory = "/home/gefen/Website-Eye-Robot/TESTS/REAL TESTS/SMALL_TEXT_ANNOTATED"
# test_directory(directory_path, save_directory)
# Test image
# detect_small_text("4.jpg", "SMALL_TEXT.png")
