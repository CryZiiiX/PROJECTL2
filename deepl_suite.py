import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
# pip install google-generativeai
import deepl
# pip install deepl
from config import GOOGLE_API_KEY, DEEPL_API_KEY1, DEEPL_API_KEY2
from bdd_SQL_V4 import *

def main():
    # étape 1 : simulation d'une entrée pour une facture
    # les données suivantes seront fournies par le système expert et l'UI
    date_facture = "2024-04-28"
    emetteur = "Exemple Émetteur"
    montant_original = 1200.50
    devise_originale = "USD"
    montant_euros = 1100.45  # la conversion a déjà été faite
    categorie = "Technologie"
    test = 1  # on marque comme test pour pouvoir supprimer facilement de la bdd

    # étape 2 : on enregistre la facture
    id_facture = bouton_valider_donnees_enregistre_facture(date_facture, emetteur,
                                                           montant_original, devise_originale,
                                                           montant_euros, categorie, test)
    print("\n")
    print(f"ID de la facture enregistrée: {id_facture}")
    print("\n")

    # impression des détails de la facture enregistrée
    afficher_informations_facture(id_facture)
    print("\n")

    # étape 3 : chemin du fichier à traiter (après extraction Tesseract)
    chemin_fichier_intermediaire_post_rectangle = "facture14_text.txt"

    # étape 4 : nettoyage du texte avec Gemini
    texte_nettoye = bouton_langue_dans_laquelle_traduire(chemin_fichier_intermediaire_post_rectangle)
    print("\n")
    print(f"Texte nettoyé: {texte_nettoye}")
    print("\n")

    # étape 5 : traduction du texte
    langue_cible = "anglais"  # l'utilisateur veut traduire le texte en anglais
    texte_traduit = bouton_valider_texte(texte_nettoye, langue_cible, id_facture)
    # impression des détails de la facture enregistrée
    afficher_informations_facture(id_facture)
    print("\n")
    print(f"Texte traduit: {texte_traduit}")

    # étape 6 : écriture de la traduction dans un fichier
    nom_fichier = "resultats_traduction.txt"
    ecrire_dans_fichier(nom_fichier, texte_traduit)
    # on supprime les données relatives aux tests (on perd donc le nb de caractères traduits)
    supprimer_test()




def bouton_valider_donnees_enregistre_facture(date_facture, emetteur, montant_original, devise_originale, montant_euros, categorie, test):
    """
    Enregistre les données de la facture dans la base de données.
    Arguments :
        date_facture (str) : La date de la facture au format YYYY-MM-DD.
        emetteur (str) : Le nom de l'émetteur de la facture.
        montant_original (float) : Le montant de la facture dans la devise originale.
        devise_originale (str) : La devise de la facture.
        montant_euros (float) : Le montant de la facture converti en euros.
        categorie (str) : Catégorie de la facture.
        test (int) : Valeur 1 si c'est un test, autrement non spécifié.
    Retourne :
        int: L'ID de la facture enregistrée.
    """

    # on récupère la connexion et le curseur
    connection, cursor = connect_to_db()

    # on récupère l'ID de la facture lors de son ajout à la BDD
    id_facture = enregistrer_facture(connection, cursor, date_facture, emetteur, montant_original, devise_originale, montant_euros, categorie, test)

    # ferme la connexion et le curseur
    fermeture_bdd(connection, cursor)

    # on renvoie l'ID pour éventuelle réutilisation (traduction)
    return id_facture


def bouton_langue_dans_laquelle_traduire(chemin_fichier_intermediaire_post_rectangle):
    """
    Prépare un texte pour traduction en nettoyant le texte extrait par OCR.
    Argument :
        chemin_fichier_intermediaire_post_rectangle (str): Chemin vers le fichier texte intermédiaire contenant
        l'extraction initiale de Tesseract avant post traitement (tel qu'obtenu après tracé des rectangles)
    Retourne :
        str: Texte nettoyé prêt pour la traduction.
    """
    # on nettoie le texte brut de Tesseract grâce à Gemini
    texte_nettoye_par_gemini = correction_par_gemini_fichier_obtenu_de_tesseract(chemin_fichier_intermediaire_post_rectangle)

    # on nettoie les résultats de Gemini (suppression des **, à voir si pertinent)
    texte_corrige_sans_bold = supprimer_etoiles(texte_nettoye_par_gemini)

    # on renvoie le texte nettoyé
    return texte_corrige_sans_bold

    ## Suite à ça, il faudra rajouter la logique avec post traitement de l'utilisateur
    ## correction éventuelle etc



def correction_par_gemini_fichier_obtenu_de_tesseract(chemin_fichier_intermediaire_post_rectangle):
    """
    Lit et corrige un fichier texte à l'aide de l'API Google Gemini.
    Argument :
        chemin_fichier_intermediaire_post_rectangle (str): Chemin vers le fichier texte.
    Retourne :
        str: Texte corrigé ou None si une erreur survient.
    """
    try:
        # on extrait le texte du fichier
        with open(chemin_fichier_intermediaire_post_rectangle, 'r', encoding='utf-8') as fichier:
            texte = fichier.read()

        # on appelle la fonction corriger_texte pour traiter le texte extrait
        texte_corrige = corriger_texte(texte)

        # on retourne le texte traité
        return texte_corrige

    # gestion des erreurs
    except FileNotFoundError:
        print(f"Le fichier {chemin_fichier_intermediaire_post_rectangle} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")
        return None


def corriger_texte(texte):
    """
    Utilise l'API Google Gemini pour corriger le texte.
    :param texte: Le texte à corriger.
    :param type_document: Le type de document à traiter (facture ou menu).
    :return: Le texte corrigé.
    """

    # configuration de l'API avec la clé du fichier
    genai.configure(api_key=GOOGLE_API_KEY)
    # accès à l'API
    modele = genai.GenerativeModel('gemini-pro')

    prompt = (f"Ce document est une facture, corrigez toutes les fautes d'orthographe, de grammaire, les "
              f"caractères superflus et les mots incorrects ou incohérents dans le texte suivant : '{texte}'."
              f" Renvoyez le texte corrigé en conservant la mise en forme initiale, y compris les espacements "
              f"des colonnes. Ajustez les sauts de ligne pour assurer une cohérence et une uniformité.")

    reponse = modele.generate_content(prompt,
                                      safety_settings={
                                          HarmCategory.HARM_CATEGORY_HATE_SPEECH:
                                              HarmBlockThreshold.BLOCK_ONLY_HIGH,
                                          HarmCategory.HARM_CATEGORY_HARASSMENT:
                                              HarmBlockThreshold.BLOCK_ONLY_HIGH, })
    # configuration des paramètres de sécurité

    try:
        # on récupère le texte corrigé par Gemini
        texte_corrige = reponse.text
        # on le renvoie
        return texte_corrige

    # gestion des erreurs
    except ValueError as e:
        print(f"Une erreur est survenue : {e}")
        if not reponse.candidates:
            print("Aucune réponse n'a été renvoyée.")
            print(f"Retour sur l'invite : {reponse.prompt_feedback}")
        return None


def supprimer_etoiles(texte):
    """
    Supprime les caractères d'étoiles utilisés pour le formatage dans le texte.
    Argument :
        texte (str): Le texte à nettoyer.
    Retourne :
        str: Texte nettoyé.
    """

    # on supprime les étoiles du texte
    texte = texte.replace('**', '').replace('*', '')
    # on renvoie le texte nettoyé
    return texte


def bouton_valider_texte(texte_a_trad, langue_cible, id_facture):
    """
    Traduit le texte et l'enregistre dans la base de données.
    Arguments :
        texte_a_trad (str): Texte à traduire. [à voir si on utilise plutôt un fichier]
        langue_cible (str): Langue dans laquelle traduire.
        id_facture (int): ID de la facture associée.
    """

    # on traduit le texte
    texte_traduit = traduire_texte(texte_a_trad, langue_cible);

    # on récupère la connexion et le curseur
    connection, cursor = connect_to_db()

    # on enregistre la traduction dans la base de données (on passe texte_a_trad en
    # argument car c'est d'après le texte original qu'on compte le nombre de caractères traduits)
    traduction_facture(id_facture, connection, cursor, langue_cible, texte_a_trad)

    # ferme la connexion et le curseur
    fermeture_bdd(connection, cursor)

    # on renvoie le texte traduit (à voir ce qu'on en fait, dans un fichier?)
    return texte_traduit


def traduire_texte(texte, langue_cible):
    """
    Utilise l'API DeepL pour traduire le texte.
    Arguments :
        texte (str): Texte à traduire.
        langue_cible (str): Langue cible de la traduction.
    Retourne :
        str: Texte traduit ou un message d'erreur si les quotas sont dépassés.
    """

    # on récupère la connexion et le curseur
    connection, cursor = connect_to_db()

    # on récupère le nombre de caractères traduit durant le mois calendaire
    caracteres_trad_mois = total_caracteres_mois(cursor)
    print(f"Il y a eu {caracteres_trad_mois} caractères traduits ce mois.")

    # ferme la connexion et le curseur
    fermeture_bdd(connection, cursor)

    # selon le nombre de caractères traduits, on choisit notre clé d'API
    if caracteres_trad_mois < 495000:
        cle_API = DEEPL_API_KEY1
    elif caracteres_trad_mois < 995000:
        cle_API = DEEPL_API_KEY2
    else:
        return "Caractères épuisés pour le mois."

    # configuration de l'API avec la clé et création d'une instance translator
    translator = deepl.Translator(cle_API)

    # on choisit la bonne option de langue à passer à l'API selon notre choix de langue_cible
    lang_cible = {'anglais': "EN-US", 'espagnol': "ES", 'allemand': "DE"}.get(langue_cible)

    try:
        result = translator.translate_text(
            text=texte,  # texte à traduire
            source_lang="FR",  # Définit la langue source comme français
            target_lang=lang_cible,  # Définit la langue cible (anglais, espagnol ou allemand)
            preserve_formatting=True,  # Indique à l'API de préserver le formatage du texte original
            outline_detection=True,  # Indique à l'API de détecter les points d'articulation du texte
            split_sentences='1',  # Indique à l'API de diviser le texte en phrases
        )
        return result.text  # on retourne le texte traduit

    finally:
        translator.close()  # on ferme l'instance translator


def traduire_texte_fake(texte, langue_cible):
    """
    Utilise l'API DeepL pour traduire le texte.
    Arguments :
        texte (str): Texte à traduire.
        langue_cible (str): Langue cible de la traduction.
    Retourne :
        str: Texte traduit ou un message d'erreur si les quotas sont dépassés.
    """
    # on récupère la connexion et le curseur
    connection, cursor = connect_to_db()

    # on récupère le nombre de caractères traduit durant le mois calendaire
    caracteres_trad_mois = total_caracteres_mois(cursor)
    print(f"Il y a eu {caracteres_trad_mois} caractères traduits ce mois.")

    # ferme la connexion et le curseur
    fermeture_bdd(connection, cursor)

    # selon le nombre de caractères traduits, on choisit notre clé d'API
    if caracteres_trad_mois < 495000:
        cle_API = DEEPL_API_KEY1
    elif caracteres_trad_mois < 995000:
        cle_API = DEEPL_API_KEY2
    else:
        return "Caractères épuisés pour le mois."

    return texte  # on renvoie le texte d'origine


def ecrire_dans_fichier(nom_fichier, texte_traduit):
    """
    Fonction pour écrire le texte traduit dans un fichier
    :param nom_fichier: Le nom du fichier de sortie.
    :param texte_traduit: Le texte traduit.
    :return: None
    """
    with open(nom_fichier, 'w', encoding='utf-8') as fichier:
        fichier.write("Texte traduit:\n")
        fichier.write(texte_traduit + "\n\n\n")



if __name__ == "__main__":
    main()