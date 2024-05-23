import deepl
from config import DEEPL_API_KEY1, DEEPL_API_KEY2, OPENAI_API_KEY
from bdd_SQL import *
from openai import OpenAI


def bouton_valider_donnees_enregistre_facture(date_facture, emetteur, montant_original, devise_originale, montant_euros, categorie, test):
    """
    Enregistre les données de la facture dans la base de données.
    arguments :
        date_facture (str) : la date de la facture au format YYYY-MM-DD.
        emetteur (str) : le nom de l'émetteur de la facture.
        montant_original (float) : le montant de la facture dans la devise originale.
        devise_originale (str) : la devise de la facture.
        montant_euros (float) : le montant de la facture converti en euros.
        categorie (str) : catégorie de la facture.
        test (int) : valeur 1 si c'est un test, autrement non spécifié.
    Retourne :
        int: l'ID de la facture enregistrée.
    """

    # on récupère la connexion et le curseur
    connection, cursor = connect_to_db()

    # on récupère l'ID de la facture lors de son ajout à la BDD
    id_facture = enregistrer_facture(connection, cursor, date_facture, emetteur, montant_original, devise_originale, montant_euros, categorie, test)

    # ferme la connexion et le curseur
    fermeture_bdd(connection, cursor)

    # on renvoie l'ID pour éventuelle réutilisation (traduction)
    return id_facture


def nettoyage_texte(chemin_fichier_intermediaire_post_rectangle):                                    # PAS UTILISE PAR L'UI
    """
    Prépare un texte pour traduction en nettoyant le texte extrait par OCR.
    Argument :
        chemin_fichier_intermediaire_post_rectangle (str): Chemin vers le fichier texte intermédiaire
        contenant l'extraction initiale de Tesseract avant post traitement
        (tel qu'obtenu après tracé des rectangles)
    Retourne :
        str: Texte nettoyé prêt pour la traduction.
    """
    try:
        # on extrait le texte du fichier
        with open(chemin_fichier_intermediaire_post_rectangle, 'r', encoding='utf-8') as fichier:
            texte = fichier.read()

        # on appelle la fonction corriger_texte pour traiter le texte extrait
        texte_corrige = corriger_texte_fake(texte)

        # on retourne le texte traité
        return texte_corrige

    # gestion des erreurs
    except FileNotFoundError:
        print(f"Le fichier {chemin_fichier_intermediaire_post_rectangle} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")
        return None


def nettoyage_texte_txt(texte):
    """
    Prépare un texte pour traduction en nettoyant le texte extrait par OCR.
    Argument :
        str: texte contenant l'extraction initiale de Tesseract avant post traitement
        (tel qu'obtenu après tracé des rectangles)
    Retourne :
        str: Texte nettoyé prêt pour la traduction.
    """
    # on appelle la fonction corriger_texte pour traiter le texte extrait
    texte_corrige = corriger_texte_fake(texte)

    # on retourne le texte traité
    return texte_corrige


def corriger_texte(texte):
    """
    Utilise l'API de ChatGPT 3.5 turbo pour corriger le texte.
    :param texte: Le texte à corriger.
    :return: Le texte corrigé.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are an assistant with exceptional French editorial skills, "
                        "capable of identifying and correcting typographical errors in the text."},
            {"role": "user",
             "content": f"Le texte suivant est issu d'une facture."
                        f" Corrige les fautes de grammaires, les typos, les caractères isolés."
                        f" Renvoie uniquement le texte corrigé dans ta réponse : {texte}"}
        ]
    )

    reponse = completion.choices[0].message.content

    return reponse

def corriger_texte_fake(texte):
    """
    Pour ne pas épuiser les crédits openAI
    """
    reponse = texte
    return reponse


def supprimer_etoiles(texte):
    """
    Supprime les caractères d'étoiles utilisés pour le formatage dans le texte.
    argument :
        texte (str): le texte à nettoyer.
    Retourne :
        str: texte nettoyé.
    """

    # on supprime les étoiles du texte
    texte = texte.replace('**', '').replace('*', '')
    # on renvoie le texte nettoyé
    return texte


def traduction_maj_bdd(texte_a_trad, langue_cible, id_facture):
    """
    Traduit le texte et l'enregistre dans la base de données.
    Arguments :
        texte_a_trad (str): texte à traduire. [à voir si on utilise plutôt un fichier]
        langue_cible (str): langue dans laquelle traduire.
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
        texte (str): texte à traduire.
        langue_cible (str): langue cible de la traduction.
    Retourne :
        str: texte traduit ou un message d'erreur si les quotas sont dépassés.
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
            source_lang="FR",  # définit la langue source comme français
            target_lang=lang_cible,  # définit la langue cible (anglais, espagnol ou allemand)
            preserve_formatting=True,  # indique à l'API de préserver le formatage du texte original
            outline_detection=True,  # indique à l'API de détecter les points d'articulation du texte
            split_sentences='1',  # indique à l'API de diviser le texte en phrases
        )
        return result.text  # on retourne le texte traduit

    finally:
        translator.close()  # on ferme l'instance translator


def traduire_texte_fake(texte, langue_cible):
    """
    Utilise l'API DeepL pour traduire le texte.
    Arguments :
        texte (str): texte à traduire.
        langue_cible (str): langue cible de la traduction.
    Retourne :
        str: texte traduit ou un message d'erreur si les quotas sont dépassés.
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


def ecrire_dans_fichier(nom_fichier, texte, commentaire):
    """
    Fonction pour écrire le texte traduit dans un fichier
    :param nom_fichier: Le nom du fichier de sortie.
    :param texte_traduit: Le texte traduit.
    :return: None
    """
    with open(nom_fichier, 'w', encoding='utf-8') as fichier:
        fichier.write("Texte " + commentaire +":\n")
        fichier.write(texte + "\n\n\n")

