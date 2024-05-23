import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
import pytesseract

# Initialise les variables globales
rectangles = []  # liste des rectangles dessinés sur le canvas
rect_id = None  # identifiant du rectangle en cours de dessin
img_cv = None  # image chargée dans OpenCV pour le traitement
img_cv_path = None  # chemin de l'image chargée

# fonction pour importer une image depuis le système de fichiers
def import_image():
    global img_cv, img_cv_path
    file_path = filedialog.askopenfilename()  # ouvre une boîte de dialogue pour choisir un fichier
    if file_path:  # vérifie si un fichier a été sélectionné
        show_image(file_path)  # affiche l'image sélectionnée
        img_cv_path = file_path  # stocke le chemin complet de l'image
        img_cv = cv2.imread(file_path)  # charge l'image pour OpenCV

# fonction pour afficher l'image sélectionnée dans le canvas de Tkinter
def show_image(file_path):
    global photo
    image = Image.open(file_path)  # ouvre l'image avec PIL
    photo = ImageTk.PhotoImage(image)  # convertit l'image PIL en image Tkinter
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)  # place l'image au point nord-ouest du canvas

# fonction appelée lors du clic sur le canvas, pour commencer à dessiner un rectangle
def on_canvas_click(event):
    global start_x, start_y, rect_id
    start_x, start_y = event.x, event.y  # stocke la position initiale du clic
    rect_id = canvas.create_rectangle(start_x, start_y, start_x + 1, start_y + 1, outline='red')  # commence à dessiner un rectangle minuscule

# fonction appelée lors du glissement de la souris avec le bouton pressé, pour redimensionner le rectangle
def on_canvas_drag(event):
    end_x, end_y = event.x, event.y  # position actuelle de la souris
    canvas.coords(rect_id, start_x, start_y, end_x, end_y)  # met à jour les coordonnées du rectangle pour l'agrandir

# fonction appelée lors du relâchement du bouton de la souris, pour terminer le dessin du rectangle
def on_canvas_release(event):
    global rect_id
    end_x, end_y = event.x, event.y  # position finale de la souris
    if rect_id:
        coordinates = (start_x, start_y, end_x, end_y)  # finalise les coordonnées du rectangle
        rectangles.append([rect_id, coordinates])  # ajoute le rectangle à la liste
        rect_id = None  # réinitialise l'identifiant du rectangle
        print(f"Rectangle added: {coordinates}")  # affiche les coordonnées pour le debug

# fonction pour effacer le dernier rectangle ajouté
def clear_last_rectangle():
    if rectangles:  # vérifie s'il y a des rectangles à effacer
        rect_to_delete = rectangles.pop()  # enlève le dernier rectangle de la liste
        canvas.delete(rect_to_delete[0])  # efface le rectangle du canvas
        print(f"Rectangle removed: {rect_to_delete[1]}")  # affiche les coordonnées pour le debug

# fonction pour valider tous les rectangles et extraire le texte des zones correspondantes
def validate_all():
    scale_factor = 1.5  # facteur de mise à l'échelle pour le redimensionnement de l'image
    if img_cv is None:
        messagebox.showerror("Erreur", "Aucune image chargée.")  # affiche une erreur si aucune image n'est chargée
        return

    resized_img = resize_image(img_cv, scale_factor)  # redimensionne l'image
    sorted_rects = sorted(rectangles, key=lambda x: (x[1][1], x[1][0]))  # trie les rectangles par ordre vertical puis horizontal
    results = []
    for rect in sorted_rects:
        _, coords = rect
        scaled_coords = adjust_and_validate_roi(coords, scale_factor)  # ajuste les coordonnées des rectangles
        x1, y1, x2, y2 = scaled_coords
        roi_img = resized_img[y1:y2, x1:x2]  # extrait la région d'intérêt de l'image redimensionnée
        text = pytesseract.image_to_string(roi_img, config='--oem 1 --psm 6 -l fra')  # utilise pytesseract pour extraire le texte
        results.append(text)
        print(f'Text from ROI: {text}')  # affiche le texte extrait pour le debug

    # prépare le chemin de sortie pour enregistrer le fichier
    base_name = os.path.basename(img_cv_path)  # extrait le nom de base du fichier
    file_name_without_extension = os.path.splitext(base_name)[0]  # supprime l'extension
    output_file_name = f"{file_name_without_extension}_text.txt"  # construit le nom du fichier de sortie

    output_folder = "factures_integration"  # nom du dossier de sortie
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # crée le dossier s'il n'existe pas

    output_path = os.path.join(output_folder, output_file_name)  # construit le chemin complet du fichier de sortie

    with open(output_path, 'w') as file:  # ouvre le fichier en écriture
        file.write("\n".join(results))  # écrit les résultats dans le fichier
    messagebox.showinfo("Extraction terminée", f"Texte enregistré dans {output_path}")  # affiche une boîte de dialogue à la fin

# fonction pour redimensionner l'image selon un facteur de mise à l'échelle
def resize_image(image, scale_factor):
    width = int(image.shape[1] * scale_factor)  # calcule la nouvelle largeur
    height = int(image.shape[0] * scale_factor)  # calcule la nouvelle hauteur
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)  # retourne l'image redimensionnée

# fonction pour ajuster et valider les coordonnées des ROI selon le facteur de mise à l'échelle
def adjust_and_validate_roi(roi, scale_factor):
    x1, y1, x2, y2 = [int(x * scale_factor) for x in roi]  # applique le facteur de mise à l'échelle aux coordonnées du ROI
    return x1, y1, x2, y2  # retourne les coordonnées ajustées

# création de l'interface graphique principale
root = tk.Tk()
root.geometry('1368x768')  # dimension de la fenêtre
root.title("ProjectL2")  # titre de la fenêtre

canvas = tk.Canvas(root)  # crée un canvas pour dessiner et afficher l'image
canvas.pack(fill='both', expand=True)  # ajoute le canvas à la fenêtre

btn_import_image = tk.Button(root, text="Importer Image", command=import_image)  # bouton pour importer une image
btn_import_image.pack(pady=10)  # positionne le bouton

canvas.bind("<ButtonPress-1>", on_canvas_click)  # associe l'événement de clic à la fonction on_canvas_click
canvas.bind("<B1-Motion>", on_canvas_drag)  # associe le glissement de la souris avec bouton pressé à la fonction on_canvas_drag
canvas.bind("<ButtonRelease-1>", on_canvas_release)  # associe le relâchement du bouton à la fonction on_canvas_release

btn_validate = tk.Button(root, text="Valider Tout", command=validate_all)  # bouton pour valider l'extraction du texte
btn_validate.pack(side='left', padx=10)  # positionne le bouton

btn_clear = tk.Button(root, text="Effacer Dernier Rectangle", command=clear_last_rectangle)  # bouton pour effacer le dernier rectangle
btn_clear.pack(side='left', padx=10)  # positionne le bouton

root.mainloop()  # lance la boucle principale de l'interface graphique
