from PIL import Image, ImageTk
import cv2
import os
import pytesseract


# fonction pour redimensionner l'image selon un facteur de mise à l'échelle
def resize_image(image, scale_factor):
    width = int(image.shape[1] * scale_factor)  # calcule la nouvelle largeur
    height = int(image.shape[0] * scale_factor)  # calcule la nouvelle hauteur
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)  # retourne l'image redimensionnée

# fonction pour ajuster et valider les coordonnées des ROI selon le facteur de mise à l'échelle
def adjust_and_validate_roi(roi, scale_factor):
    x1, y1, x2, y2 = [int(x * scale_factor) for x in roi]  # applique le facteur de mise à l'échelle aux coordonnées du ROI
    return x1, y1, x2, y2  # retourne les coordonnées ajustées

# Fonctions pour redresser une image penchée
#Source: https://becominghuman.ai/how-to-automatically-deskew-straighten-a-text-image-using-opencv-a0c30aed83df
# Détection de l'angle
def getSkewAngle(cvImage) -> float:
    # Prépare l'image, la copie, la convertit en "grayscale", applique blur et threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Dilate le texte afin d'obtenir de faire ressortir les lignes et paragraphes
    # Applique un kernel plus grand sur l'axe X pour fusionner les caractères et obtenir une ligne compacte sans espaces
    # Applique un kernel plus petit sur l'axe Y pour bien séparer les blocs de texte
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Trouve les contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Trouve le contour le plus large et traite le
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)
    
    # Détermine l'angle et le convertir en angle de rotation par rapport à une image droite
    angle = minAreaRect[-1]
    if angle > 45:
        angle = angle - 90
    return -1.0 * angle

# Fait pivoter l'image autour de son centre
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage
