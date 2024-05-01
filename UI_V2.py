#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
#from tkcalendar import Calendar, DateEntry
from PIL import Image, ImageTk
import cv2
import os
import pytesseract
from pdf2image import convert_from_path
from sys_exp import *
from tesseract import *
from bdd_SQL_V4 import *

# Initialise les variables globales
rectangles = []  # liste des rectangles dessinés sur le canvas
rect_id = None  # identifiant du rectangle en cours de dessin
img_cv = None  # image chargée dans OpenCV pour le traitement
img_cv_path = None  # chemin de l'image chargée
issuer = None   # émetteur de la facture
date = None   # date de la facture
amount = 0   # Montant total de la facture en devise
currency = None  # devise de la facture
fx_rate = 1    # taux de change vers l'euro pour la devise donnée
amount_eur = 0     # montant total de la facture en eurors
expense_category = None   # Catégorie de dépense
language = None  # Langage vers lequel la traduction est demandée
accounting_month = None  # Mois de référence pour onglet comptabilité
accounting_year = 0  # Année de référence pour onglet comptabilité

# fonction pour importer une image depuis le système de fichiers
def import_image():
    global img_cv, img_cv_path
    file_path = filedialog.askopenfilename()  # ouvre une boîte de dialogue pour choisir un fichier
    if file_path:  # vérifie si un fichier a été sélectionné
        path, fileName = os.path.split(file_path)
        fileBaseName, fileExtension = os.path.splitext(fileName)
        if (fileExtension in [".jpg", ".jpeg", ".png", ".pdf"]):   # Vérifie le type de fichier
            if (fileExtension == ".pdf"):         
                file_path = convertitPdf(file_path)          # convertit en image s'il s'agit d'un pdf

#            image = Image.open(file_path)
            image = cv2.imread(file_path)            
            angle = getSkewAngle(image)                 # calcule l'angle de l'image pour déterminer s'il faut la redresser
            print(angle)
            if ((angle > 0.8 and angle < 45) or (angle < -0.8 and angle > -45)):
                image = rotateImage(image, -1 * angle)           # redresse l'image
                new_filePath_angle = path + '/' + fileBaseName + 'skewed' + '.jpg'
                cv2.imwrite(new_filePath_angle, image)
                file_path = new_filePath_angle
        
            show_image(file_path)  # affiche l'image sélectionnée
            img_cv_path = file_path  # stocke le chemin complet de l'image
            img_cv = cv2.imread(file_path)  # charge l'image pour OpenCV

        else:
            print("type d'image non valide") 

# fonction qui convertit un pdf en image
def convertitPdf(filePath):
    image_a_traiter = convert_from_path(filePath)
    path, fileName = os.path.split(filePath)
    fileBaseName, fileExtension = os.path.splitext(fileName)
    new_filePath = path + '/' + fileBaseName + '.jpg'
    image_a_traiter[0].save(new_filePath, 'JPEG')
    return (new_filePath)

# fonction pour afficher l'image sélectionnée dans le canvas de Tkinter
def show_image(file_path):
    global photo
    image = Image.open(file_path)  # ouvre l'image avec PIL
 #   resized_image = image.resize((580, 750))  # redimensionne l'image
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
    global issuer, date, amount, currency, amount_eur
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

    # affiche l'image dans l'onglet2
    canvas2.create_image(0, 0, anchor=tk.NW, image=photo)  # place l'image au point nord-ouest du canvas de l'onglet 2

    # prépare le chemin de sortie pour enregistrer le fichier
    base_name = os.path.basename(img_cv_path)  # extrait le nom de base du fichier
    file_name_without_extension = os.path.splitext(base_name)[0]  # supprime l'extension
    output_file_name = f"{file_name_without_extension}_text.txt"  # construit le nom du fichier de sortie

    output_folder = "factures_integration"  # nom du dossier de sortie
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # crée le dossier s'il n'existe pas

    output_path = os.path.join(output_folder, output_file_name)  # construit le chemin complet du fichier de sortie

    full_text = "\n".join(results)

    with open(output_path, 'w') as file:  # ouvre le fichier en écriture
        file.write(full_text)  # écrit les résultats dans le fichier

    messagebox.showinfo("Extraction terminée", f"Texte enregistré dans {output_path}")  # affiche une boîte de dialogue à la fin

    issuer = ''                            #  SOURCE: SYSTEME EXPERT POSSIBLE?
    issuer_label.set(issuer)
    date = extract_date(full_text)
    date_label.set(date)
    amount = extract_amount(full_text)
    amount_label.set(amount)
    currency = ''                            #  SOURCE: SYSTEME EXPERT POSSIBLE?
    currency_label.set(currency)
    fx_rate = 1                                 # SOURCE: API POSSIBLE?
    amount_eur = amount * fx_rate
    amount_eur_label.set(amount_eur)



#    tab_control.tab1.forget()
#    tab_control.tab2.tkraise()
#    tab_control.pack(expand=1,fill='both')


# fonction de validation des données principales par l'utilisateur
def validate_main_data():
    global issuer, date, amount, currency, fx_rate, amount_eur
    amount_change = 0
    currency_change = 0
    if issuer_entry.get():
        issuer = issuer_entry.get()
     # EMETTEUR OBLIGATOIRE - TEST A RAJOUTER
    if date_entry.get():
        date = date_entry.get()
    # DATE OBLIGATOIRE - TEST A RAJOUTER
    if amount_entry.get():
        amount = amount_entry.get()
    # MONTANT OBLIGATOIRE - TEST A RAJOUTER
    if currency_entry.get():
        currency = currency_entry.get()
                                 # SOURCE: API POSSIBLE?
    # DEVISE OBLIGATOIRE - TEST A RAJOUTER

    fx_rate = 1
    amount_eur = amount * fx_rate
    amount_eur_confirmed.set(amount_eur)

    # BLOQUER BOUTON VALIDATION

# fonction de validation du texte par l'utilisateur
def validate_text():
    print("fonction à écrire")
    # BOUTON POUR OUVERTURE D'UNE NOUVELLE FENETRE AVEC LE TEXTE A CORRIGER 
    # doit inclure le systeme expert déterminant la catégorie

# fonction de validation de la catégorie par l'utilisateur
def validate_category():
    global expense_category
    if expense_category_entry.get():
        expense_category = expense_category_entry.get()

    # CATEGORIE OBLIGATOIRE - TEST A RAJOUTER

    # AJOUT DE LA FACTURE DANS LA BASE DE DONNEES

    # BLOQUER BOUTON VALIDATION

# fonction de traduction
def translate():
    print("fonction à écrire")
    if language_entry.get():
        language = language_entry.get()
    else:
        messagebox.showinfo("Erreur", f"Veuillez entrer la langue vers laquelle traduire")  # affiche une boîte de dialogue

    # AJOUTER fonction de traduction avec API
    # COMPLETER INFOS FACTURE DANS LA BASE DE DONNEE
    # BLOQUER BOUTON TRADUCTION

# fonction de comptabilité (visualisation des montants par catégorie pour une période donnée)
def display_sums():
    global accounting_month, accounting_year, categorie
    if accounting_month_entry.get():
        accounting_month = accounting_month_entry.get()
    else:
        accounting_month = None

    if accounting_year_entry.get():
        accounting_year = int(accounting_year_entry.get())
        previous_accounting_year = accounting_year - 1
        tk.Label(tab4, text=accounting_year).grid(row=1,  column=1,  padx=(5,10), pady = 10)
        tk.Label(tab4, text=previous_accounting_year).grid(row=1,  column=2,  padx=(5, 10), pady = 10)
    else:
        messagebox.showinfo("Erreur", f"Veuillez entrer l'année")  # affiche une boîte de dialogue

    # récupère la connexion et le curseur
    connection, cursor = connect_to_db()

    # pour chaque catégorie de dépense:
    for i in range(len(liste_categorie_depense)):

    # définit la catégorie que l'on va rechercher
        categorie = liste_categorie_depense[i]
    # stocke le résultat pour une catégorie dans une variable (année n et n-1)
        somme_montant_cat_year = somme_factures_categorie(accounting_month, accounting_year, categorie, cursor)
        somme_montant_cat_prev_year = somme_factures_categorie(accounting_month, accounting_year, categorie, cursor)

    # vérifie que le montant total est un float (car montant est de type FLOAT) non négatif         # A REVOIR
  #  assert isinstance(somme_montant_cat_year, float) and somme_montant_cat_year >= 0.0, "Le montant total par catégorie doit être un flottant non négatif"
   # assert isinstance(somme_montant_cat_prev_year, float) and somme_montant_cat_prev_year >= 0.0, "Le montant total par catégorie doit être un flottant non négatif"

        # met à jour l'onglet 4
        tk.Label(tab4, text=categorie).grid(row=i+2,  column=0,  padx=(200, 0), pady = 5)
        tk.Label(tab4, text=somme_montant_cat_year).grid(row=i+2,  column=1,  padx=(5, 10), pady = 5)
        tk.Label(tab4, text=somme_montant_cat_prev_year).grid(row=i+2,  column=2,  padx=(5, 10), pady = 5)

    #AJOUTER LA SOMME DES CATEGORIES
    # AJOUTER BOUTONS PERMETTANT DE VOIR LE DETAIL DES FACTURES POUR CHAQUE CATEGORIE

    # ferme la connexion et le curseur
    fermeture_bdd(connection, cursor)



# création de l'interface graphique principale
root = tk.Tk()
root.geometry('1368x768')  # dimension de la fenêtre
root.title("ProjectL2")  # titre de la fenêtre

tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)
tab5 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Affichage Image")
tab_control.add(tab2, text="Vérification")
tab_control.add(tab3, text="Traduction - Maxime")
tab_control.add(tab4, text="Comptabilité")
tab_control.add(tab5, text="Statistiques - Maxime")

# AJOUTER PASSAGE D'UN ONGLET A UN AUTRE AVEC SUPPRESSION DE L'IMAGES ET DES INFORMATIONS PRECEDENTES SUR TOUS LES ONGLETS

# création de l'onglet "Affichage Image" (Onglet 1)

#canvas = tk.Canvas(tab1, bg = "blue") # crée un canvas pour dessiner et afficher l'image       # RETIRER LA COULEUR (POUR TESTS)
canvas = tk.Canvas(tab1) # crée un canvas pour dessiner et afficher l'image  
canvas.grid(row=0, column=0, sticky="nsew")

#right_frame = tk.Frame(tab1, bg = "green")                                                     # RETIRER LA COULEUR (POUR TESTS)
right_frame = tk.Frame(tab1)                                     
right_frame.grid(row=0, column=1, sticky="new")

tab1.columnconfigure(0, weight = 5)     # répartit les colonnes équitablement
tab1.columnconfigure(1, weight = 1)

tk.Button(right_frame, text="Importer Image", command=import_image).grid(row=0,  column=0,  padx=(150,10),  pady=(50,10))  # bouton pour importer une image

canvas.bind("<ButtonPress-1>", on_canvas_click)  # associe l'événement de clic à la fonction on_canvas_click
canvas.bind("<B1-Motion>", on_canvas_drag)  # associe le glissement de la souris avec bouton pressé à la fonction on_canvas_drag
canvas.bind("<ButtonRelease-1>", on_canvas_release)  # associe le relâchement du bouton à la fonction on_canvas_release

tk.Button(right_frame, text="Effacer Dernier Rectangle", command=clear_last_rectangle).grid(row=1,  column=0,  padx=(150,10), pady=(50,10))  # bouton pour effacer le dernier rectangle

tk.Button(right_frame, text="Valider Tout", command=validate_all).grid(row=2,  column=0,  padx=(150,10),  pady=(500,10))  # bouton pour valider l'extraction du texte


# création de l'onglet "Vérification" (Onglet 2)

# Visualisation de la facture

#canvas2 = tk.Canvas(tab2, bg = "blue") # crée un canvas pour dessiner et afficher l'image       # RETIRER LA COULEUR (POUR TESTS)
canvas2 = tk.Canvas(tab2) # crée un canvas pour dessiner et afficher l'image  
canvas2.grid(row=0, column=0, sticky="nsew")

#right_frame2 = tk.Frame(tab2, bg = "green")                                                     # RETIRER LA COULEUR (POUR TESTS)
right_frame2 = tk.Frame(tab2)                                         
right_frame2.grid(row=0, column=1, sticky="ne")

tab2.columnconfigure(0, weight = 5)     # répartit les colonnes équitablement
tab2.columnconfigure(1, weight = 1)

padding_x_0 = (10,0)
padding_x_1 = (5,0)
padding_x_2 = (5,20)
padding_y_fin = (5,20)

# Colonnes "proposé" et "corrigé"
tk.Label(right_frame2, text="Proposé").grid(row=0,  column=1,  padx=padding_x_1,  pady=padding_y_fin)
tk.Label(right_frame2, text="Corrigé").grid(row=0,  column=2,  padx=padding_x_2,  pady=padding_y_fin)

# Emetteur de la facture:
tk.Label(right_frame2, text="Emetteur de la facture:").grid(row=1,  column=0,  padx=padding_x_0,  pady=padding_y_fin)
issuer_label = tk.StringVar(value=None)
tk.Label(right_frame2, textvariable=issuer_label).grid(row=1,  column=1, padx=padding_x_1, pady=padding_y_fin)
(issuer_entry := tk.Entry(right_frame2)).grid(row=1,  column=2,  padx=padding_x_2,  pady=padding_y_fin)

# Date de la facture:
tk.Label(right_frame2, text="Date de la facture:").grid(row=2, column=0, padx=padding_x_0, pady=padding_y_fin)
date_label = tk.StringVar(value=None)
tk.Label(right_frame2, textvariable=date_label).grid(row=2,  column=1, padx=padding_x_1, pady=padding_y_fin)
(date_entry := tk.Entry(right_frame2)).grid(row=2,  column=2, padx=padding_x_2, pady=padding_y_fin)

#input_date.pack(padx=(100,0))                  # NE FONCTIONNE PAS, A CREUSER
#cal = Calendar(top,
#    font="Arial 14", selectmode='day',
#    cursor="hand1", year=2018, month=2, day=5)
#cal.pack(fill="both", expand=True)

# Montant et devise de la facture:
tk.Label(right_frame2, text="Montant:").grid(row=3,  column=0,  padx=padding_x_0,  pady=5)
amount_label = tk.StringVar(value=0)
tk.Label(right_frame2, textvariable=amount_label).grid(row=3,  column=1,  padx=padding_x_1,  pady=5)
(amount_entry := tk.Entry(right_frame2)).grid(row=3,  column=2,  padx=padding_x_2,  pady=5)

tk.Label(right_frame2, text="Devise:").grid(row=4,  column=0,  padx=padding_x_0,  pady=5)
currency_label = tk.StringVar(value=None)
tk.Label(right_frame2, textvariable=currency_label).grid(row=4,  column=1,  padx=padding_x_1,  pady=5)
liste_devises	= ('EUR', 'USD', 'CAD')                   # LISTE A COMPLETER
(currency_entry := ttk.Combobox(right_frame2, values = liste_devises)).grid(row=4,  column=2,  padx=padding_x_2,  pady=5)

# Affichage du montant en euros, pour information
tk.Label(right_frame2, text="Montant en EUR:").grid(row=5,  column=0,  padx=padding_x_0,  pady=padding_y_fin)
amount_eur_label = tk.StringVar(value=0)
tk.Label(right_frame2, textvariable=amount_eur_label).grid(row=5,  column=1,  padx=padding_x_1,  pady=padding_y_fin)
amount_eur_confirmed = tk.StringVar(value=0)
tk.Label(right_frame2, textvariable=amount_eur_confirmed).grid(row=5,  column=2,  padx=padding_x_2,  pady=padding_y_fin)

tk.Button(right_frame2,  text="Valider données",  command=validate_main_data).grid(row=6,  column=1,  padx=padding_x_1,  pady=padding_y_fin)

# Texte:                                                                                                # A AGRANDIR
tk.Label(right_frame2, text="Texte:").grid(row=7,  column=0,  padx=padding_x_0,  pady=5)
tk.Entry(right_frame2).grid(row=7,  column=1,  padx=padding_x_1,  pady=5)
tk.Button(right_frame2,  text="Valider texte",  command=validate_text).grid(row=8,  column=1,  padx=padding_x_1,  pady=padding_y_fin)


# Catégorie de dépense:
tk.Label(right_frame2, text="Catégorie de dépense:").grid(row=10,  column=0,  padx=padding_x_0,  pady=5)
expense_category_label = tk.StringVar(value=None)
tk.Label(right_frame2, textvariable=expense_category_label).grid(row=10,  column=1,  padx=padding_x_1,  pady=5)
liste_categorie_depense	= ('Logement','Transport','Assurances','Santé', 'Ameublement', 'Téléphonies', 'Prêt-à-porter', 'Alimentaire', 'Frais bancaires', 'Facture - Autre', 'Inconnu')                    # LISTE A COMPLETER
(expense_category_entry := ttk.Combobox(right_frame2, values = liste_categorie_depense)).grid(row=10,  column=2,  padx=padding_x_2,  pady=5)
tk.Button(right_frame2,  text="Valider catégorie",  command=validate_category).grid(row=11,  column=1,  padx=padding_x_1,  pady=padding_y_fin)


# Traduction:
label_langues = tk.Label(right_frame2, text="Traduire en:").grid(row=13,  column=0,  padx=padding_x_0,  pady=(200,5))
liste_langues	= ('anglais', 'espagnol', 'allemand')
(language_entry := ttk.Combobox(right_frame2, values = liste_langues)).grid(row=13,  column=1,  padx=padding_x_1,  pady=(200,5))
tk.Button(right_frame2,  text="Traduire", command=translate).grid(row=14,  column=1,  padx=padding_x_1,  pady=padding_y_fin)


# création de l'onglet "Comptabilité" (Onglet 4)

image_frame = tk.Frame(tab4)

# Menu déroulant pour sélectionner l'année et (optionel) le mois:

label_mois = tk.Label(tab4, text="Mois:").grid(row=0,  column=0,  padx=(200,0),  pady=30)
liste_mois	= ('tous', 'janvier', 'février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre',)
(accounting_month_entry := ttk.Combobox(tab4, values = liste_mois)).grid(row=0,  column=1,  padx=(5, 10), pady = 30)

label_annee = tk.Label(tab4, text="Année:").grid(row=0,  column=2,  padx=(10,0),  pady=30)
liste_annees	= (2020, 2021, 2022, 2023, 2024)
(accounting_year_entry := ttk.Combobox(tab4, values = liste_annees)).grid(row=0,  column=3,  padx=(5, 10), pady = 30)

tk.Button(tab4,  text="Afficher les montants",  command=display_sums).grid(row=0,  column=4,  padx=(30,10), pady = 30)



tab_control.pack(expand=1,fill='both')

root.mainloop()  # lance la boucle principale de l'interface graphique