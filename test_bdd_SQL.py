import unittest
from bdd_SQL import *

class TestStringMethods(unittest.TestCase):


    def test_connect_to_db(self):

        print("Testing connect_to_db")

        # on récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # on vérifie qu'on est bien connecté
        assert connection.is_connected(), "La connexion à la base de données a échoué"

        # on ferme le curseur
        cursor.close()
        # on ferma la connexion
        connection.close()


    def test_enregistrer_facture(self):

        print("Testing enregistrer_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # on enregistre une facture et on récupère son ID
        facture_id = enregistrer_facture(connection, cursor, '2024-01-01', None,
                                         100.0,'EUR',100,
                                         'Service', 1)

        # recherche la facture dans la base de données
        cursor.execute("SELECT * FROM factures WHERE id = %s", (facture_id,))
        # récupère la première ligne de la réponse
        data = cursor.fetchone()

        # vérifie que la facture a été correctement enregistrée
        assert data is not None, "La facture n'a pas été enregistrée correctement"
        # affiche les détails de la facture
        print(f"Facture enregistrée : ID={data[0]}, Date Ajout dans la BDD={data[1]}, "
              f"Date de la facture={data[2]}, "
              f"Emetteur={data[3]}, Montant original={data[4]}, Devise originale={data[5]}, "
              f"Montant en euros={data[6]}, catégorie={data[7]}")

        # on supprime les entrées qui correspondant à des tests
        supprimer_test()
        # on ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_traduction_facture(self):

        print("Testing traduction_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # appelle la fonction pour enregistrer une facture et récupère l'ID de la facture
        facture_id = enregistrer_facture(connection, cursor, '2024-01-01', None,
                                         100.0,'EUR',100,
                                         'Service', 1)
        # on crée une variable texte
        texte = 'Exemple de texte à traduire'
        # on obtient sa longueur
        len_texte = len(texte)

        # on enregistre les données relatives à la traduction de la facture enregistrée
        traduction_facture(facture_id, connection, cursor, 'Anglais', texte)
        # recherche la facture dans la base de données
        cursor.execute("SELECT * FROM factures WHERE id = %s", (facture_id,))
        # récupère la première ligne de la réponse
        data = cursor.fetchone()



        # vérifie que les données de traduction sont correctes
        assert data[8] == (len_texte), "La mise à jour de la traduction a échoué"
        assert data[9] == ('Anglais'), "La mise à jour de la traduction a échoué"
        # affiche les détails de la facture après l'ajout de la traduction
        print(f"Facture enregistrée : ID={data[0]}, Date Ajout dans la BDD={data[1]}, "
              f"Date de la facture={data[2]}, "
              f"Emetteur={data[3]}, Montant original={data[4]}, Devise originale={data[5]}, "
              f"Montant en euros={data[6]}, catégorie={data[7]}, Nombre de caractères traduits="
              f"{data[8]}, Langue Cible={data[9]}")

        # on supprime les entrées de la table qui correspondent à des tests
        supprimer_test()
        # on ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_nb_facture_traitees(self):

        print("Testing nb_facture_traitees")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # calcule le nombre de factures traitées pour le mois
        traitees = nb_facture_traitees("janvier", 2024, cursor)

        # affiche le nombre de factures traitées
        print(f"Nombre de factures traitées en janvier 2024: {traitees}")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_nb_facture_traitees_null(self):

        print("Testing nb_facture_traitees null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # calcule le nombre de factures traitées pour le mois
        traitees = nb_facture_traitees(None, 2022, cursor)

        # affiche le nombre de factures traitées
        print(f"Nombre de factures traitées en 2024: {traitees}")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_prix_moyen_facture(self):

        print("Testing prix_moyen_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 2 nouvelles factures
        enregistrer_facture(connection, cursor, '2024-04-01', 'Carrefour',
                            213.4,'EUR', 213.4,
                            'Service', 1)
        enregistrer_facture(connection, cursor, '2024-04-23', None,
                            1287.2,'EUR', 1287.2,
                            'Travaux', 1)

        # calcule le prix moyen des factures pour le mois
        prix_moyen = prix_moyen_facture('avril', 2024, cursor)

        # affiche le prix moyen des factures
        print(f"Prix moyen des factures en avril 2024: {prix_moyen} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_prix_moyen_facture_null(self):

        print("Testing prix_moyen_facture_null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # calcule le prix moyen des factures pour le mois
        prix_moyen = prix_moyen_facture('avril', 2021, cursor)

        # affiche le prix moyen des factures
        print(f"Prix moyen des factures en avril 2021: {prix_moyen} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)

    def test_prix_moyen_facture_categorie(self):

        print("testing prix_moyen_facture_categorie")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 3 nouvelles factures
        enregistrer_facture(connection, cursor, '2023-04-01', None,
                            100.0,'EUR', 100.0,
                            'Service', 1)
        enregistrer_facture(connection, cursor, '2023-12-23', None,
                            1287.2,'EUR', 1287.2,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2023-11-18', 'SCI Dauphine',
                            658.5,'EUR', 658.5,
                            'Travaux', 1)

        # définit la catégorie que l'on va rechercher
        categorie = 'Travaux'
        # stocke le résultat du prix moyen pour une catégorie dans une variable
        prix_moyen_cat = prix_moyen_facture_categorie(None, 2023, categorie, cursor)

        # affiche le prix moyen des factures d'une catégorie
        print(f"Prix moyen des factures de catégorie {categorie} en 2023: {prix_moyen_cat} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_prix_moyen_facture_categorie_null(self):

        print("testing prix moyen d'une facture d'une catégorie - null ")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # définit la catégorie que l'on va rechercher
        categorie = 'Travaux'
        # stocke le résultat du prix moyen pour une catégorie dans une variable
        prix_moyen_cat = prix_moyen_facture_categorie(None, 2022, categorie, cursor)

        # affiche le prix moyen des factures d'une catégorie
        print(f"Prix moyen des factures de catégorie {categorie} en 2022: {prix_moyen_cat} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)

    def test_prix_moyen_facture_toute_categorie(self):

        print("testing prix moyen facture - toutes categories")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 3 nouvelles factures
        enregistrer_facture(connection, cursor, '2024-04-01', None,
                            100.0,'EUR', 100.0,
                            'Service', 1)
        enregistrer_facture(connection, cursor, '2024-02-23', None,
                            1287.2, 'EUR', 1287.2,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2024-03-23', None,
                            471.2,'EUR', 471.2,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2024-01-18', 'Amazon',
                            658.5,
                            'EUR', 658.5, 'Achat', 1)
        enregistrer_facture(connection, cursor, '2024-01-24', 'Le Bon Coin',
                            75.5,'EUR', 75.5,
                            'Achat', 1)

        # définit la catégorie que l'on va rechercher
        categorie = 'Travaux'
        # stocke le résultat du prix moyen pour une catégorie dans une variable
        prix_moyen_toutes_cat = prix_moyen_toutes_categories(None, 2024, cursor)

        # affiche le prix moyen des factures d'une catégorie
        print(f"Prix moyen des factures de toutes les catégories en 2024: {prix_moyen_toutes_cat} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_prix_moyen_facture_toute_categorie_null(self):

        print("testing prix moyen des factures - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # définit la catégorie que l'on va rechercher
        categorie = 'Travaux'
        # stocke le résultat du prix moyen pour une catégorie dans une variable
        prix_moyen_toutes_cat = prix_moyen_toutes_categories(None, 2020, cursor)

        # affiche le prix moyen des factures d'une catégorie
        print(f"Prix moyen des factures de toutes les catégories en 2020: {prix_moyen_toutes_cat} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_nb_caracteres_traduits(self):

        print("testing nb_caracteres_traduits")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # on enregistre 2 factures et on ajoute les données relatives à leur traduction
        facture_id = enregistrer_facture(connection, cursor, '2024-02-11', None,
                                         100.0,'EUR', 100.0,
                                         'Service', 1)
        traduction_facture(facture_id, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')
        facture_id2 = enregistrer_facture(connection, cursor, '2024-02-07',
                                          'Maison du Monde',85.0,
                                          'EUR', 85.0,
                                          'Maison', 1)
        traduction_facture(facture_id2, connection, cursor, 'Allemand',
                           'Le temps est couvert ce matin.')

        # appelle la fonction pour calculer le nombre total de caractères traduits
        total_caracteres = nb_caracteres_traduits('avril', 2024, cursor)

        # affiche le résultat pour vérification
        print(f"Nombre total de caractères traduits en avril 2024: {total_caracteres}")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_nb_caracteres_traduits_null(self):

        print("Testing nb_caracteres_traduits - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # appelle la fonction pour calculer le nombre total de caractères traduits
        total_caracteres = nb_caracteres_traduits('mai', 2000, cursor)

        # affiche le résultat pour vérification
        print(f"Nombre total de caractères traduits en mai 2000: {total_caracteres}")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)

    def test_frequence_toutes_langues_cibles(self):

        print("testing fréquence_toutes_langues_cibles")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # calcule la fréquence d'utilisation de la langue donnée
        freq_langue = frequence_toutes_langues_cibles(None, 2024, cursor)

        # affiche le résultat pour vérification
        print(f"Fréquence (%) de toutes les langues cibles en 2024: {freq_langue}")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_frequence_toutes_langues_cibles_null(self):

        print("testing fréquence_toutes_langues_cibles - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # calcule la fréquence d'utilisation de la langue donnée
        freq_langue = frequence_toutes_langues_cibles(None, 2023, cursor)

        # affiche le résultat pour vérification
        print(f"Fréquence (%) de toutes les langues cibles en 2023: {freq_langue}%")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_somme_factures_categorie(self):

        print("testing sommes_factures_categorie")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 3 nouvelles factures
        enregistrer_facture(connection, cursor, '2023-04-01', None,
                            100.0,'EUR', 100.0,
                            'Service', 1)
        enregistrer_facture(connection, cursor, '2023-12-23', None,
                            1287.2,'EUR', 1287.2,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2023-11-18', 'Julie Petit',
                            658.5,'EUR', 658.5,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-05-23', 'Decathlon',
                            170.0,'EUR', 170.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-05-11', 'Carrefour',
                            244.40,'EUR', 244.40,
                            'Service', 1)
        enregistrer_facture(connection, cursor, '2022-05-12', 'H&M',
                            852.11,'EUR', 852.11,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-05-13', 'Pierre',
                            41.25,'EUR', 41.25,
                            'Achat', 1)
        enregistrer_facture(connection, cursor, '2023-05-14', None,
                            152.34,'EUR', 152.34,
                            'Achat', 1)

        # définit la catégorie que l'on va rechercher
        categorie = 'Travaux'
        # stocke le résultat du prix moyen pour une catégorie dans une variable
        somme_montant_cat = somme_factures_categorie(None, 2022, categorie, cursor)

        # affiche le prix moyen des factures d'une catégorie
        print(f"Montant total des factures de catégorie {categorie} en 2023: {somme_montant_cat} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)

    def test_somme_factures_categorie_null(self):

        print("testing somme_facture_categorie - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # définit la catégorie que l'on va rechercher
        categorie = 'Travaux'
        # stocke le résultat du prix moyen pour une catégorie dans une variable
        somme_montant_cat = somme_factures_categorie(None, 2019, categorie, cursor)

        # affiche le prix moyen des factures d'une catégorie
        print(f"Montant total des factures de catégorie {categorie} en 2022: {somme_montant_cat} €")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_caracteres_trad_ce_mois(self):


        print("testing caracteres_trad_ce_mois")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 4 factures et les données relatives à leur traduction
        facture_id1 = enregistrer_facture(connection, cursor, '2022-04-11', None,
                                          100.0,'EUR',100.0,
                                          'Service', 1)
        traduction_facture(facture_id1, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')
        facture_id2 = enregistrer_facture(connection, cursor, '2022-05-13',
                                          'Amazon',150.0, 'EUR',
                                          150.0, 'Travaux', 1)
        traduction_facture(facture_id2, connection, cursor, 'Espagnol', 'Je dis bonjour')
        facture_id3 = enregistrer_facture(connection, cursor, '2022-06-20', 'Le Bon Coin',
                                          199.0, 'EUR', 199.0,
                                          'Travaux', 1)
        traduction_facture(facture_id3, connection, cursor, 'Allemand', 'Je dis bonjour')
        facture_id4 = enregistrer_facture(connection, cursor, '2022-07-11', 'Bricorama',
                                          100.0, 'EUR', 100.0,
                                          'Service', 1)
        traduction_facture(facture_id4, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')

        # récupère le nombre de caractères traduits
        caracteres_mois = total_caracteres_mois(cursor)

        # affiche le résultat pour vérification
        print(f"Nombre de caractères traduits ce mois: {caracteres_mois}%")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_caracteres_trad_ce_mois_null(self):

        print("testing caracteres_trad_ce_mois - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère le nombre de caractères traduits
        caracteres_mois = total_caracteres_mois(cursor)

        # affiche le résultat pour vérification
        print(f"Nombre de caractères traduits ce mois: {caracteres_mois}%")

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)




    def test_afficher_info_facture(self):

        print("testing afficher_info_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 1 facture
        facture_id1 = enregistrer_facture(connection, cursor, '2022-04-11', None,
                                          100.0,'EUR',100.0,
                                          'Service', 1)

        # on récupère et on affiche les informations de la facture
        resultat = afficher_informations_facture(cursor, facture_id1)
        print(resultat)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_details_factures_categories(self):

        print("testing details_factures_categories")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 4 factures et les données relatives à leur traduction
        facture_id1 = enregistrer_facture(connection, cursor, '2022-04-11', None,
                                          100.0,'EUR',100.0,
                                          'Service', 1)
        traduction_facture(facture_id1, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')
        facture_id2 = enregistrer_facture(connection, cursor, '2022-05-13', 'Amazon',
                                          150.0, 'EUR', 150.0,
                                          'Travaux', 1)
        traduction_facture(facture_id2, connection, cursor, 'Espagnol', 'Je dis bonjour')
        facture_id3 = enregistrer_facture(connection, cursor, '2022-06-20', 'Le Bon Coin',
                                          199.0, 'EUR', 199.0,
                                          'Service', 1)
        traduction_facture(facture_id3, connection, cursor, 'Allemand', 'Je dis bonjour')
        facture_id4 = enregistrer_facture(connection, cursor, '2022-07-11', 'Bricorama',
                                          100.0, 'EUR', 100.0,
                                          'Service', 1)
        traduction_facture(facture_id4, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')

        # récupère le détails de toutes les factures
        details = details_factures_categorie('Service', None, '2022', cursor)

        print(details)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)




    def test_details_factures_categories_null(self):

        print("testing details_factures_categories - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère le détails de toutes les factures
        details = details_factures_categorie('Service', None, '2022', cursor)

        print(details)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_compte_conversion_devise(self):

        print("testing compte_conversion_devise")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 4 factures
        enregistrer_facture(connection, cursor, '2022-04-11', None, 100.0,
                                          'USD', 100.0,  'Service',
                            1)
        enregistrer_facture(connection, cursor, '2022-04-13', 'Amazon',
                                          150.0, 'COP', 150.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-04-20', 'Le Bon Coin',
                                          199.0, 'MXN', 199.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-04-11', 'Bricorama',
                                          100.0, 'EUR', 100.0,
                            'Service', 1)

        # récupère le détail du compte des conversions de devises
        resultat = compte_conversion_devise('avril', '2022', cursor)

        print("Nombre de conversions de devises effectuées en avril 2022:", resultat)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_compte_conversion_devise_null(self):

        print("testing compte_conversion_devise - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère le détail du compte des conversions de devises
        resultat = compte_conversion_devise('avril', '2022', cursor)

        print("Nombre de conversions de devises en avril 2022:", resultat)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_compte_conversion_devise_mois(self):

        print("testing compte_conversion_devise_mois")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 4 factures
        enregistrer_facture(connection, cursor, '2024-05-11', None,
                            100.0,'USD', 100.0,
                            'Service', 1)
        enregistrer_facture(connection, cursor, '2024-05-13', 'Amazon',
                                          150.0, 'COP', 150.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2024-05-20', 'Le Bon Coin',
                                          199.0, 'MXN', 199.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2024-05-11', 'Bricorama',
                                          100.0, 'EUR', 100.0,
                            'Service', 1)

        # récupère le détail du compte des conversions de devises
        resultat = compte_conversion_devise_mois(cursor)

        print("Nombre de conversions de devises effectuées ce mois:", resultat)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_categorie_plus_frequente(self):

        print("testing categorie_plus_frequente")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 4 factures
        enregistrer_facture(connection, cursor, '2022-04-11', None, 100.0,
                                          'USD', 100.0,  'Service',
                            1)
        enregistrer_facture(connection, cursor, '2022-04-13', 'Amazon',
                                          150.0, 'COP', 150.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-04-20', 'Le Bon Coin',
                                          199.0, 'MXN', 199.0,
                            'Travaux', 1)
        enregistrer_facture(connection, cursor, '2022-04-11', 'Bricorama',
                                          100.0, 'EUR', 100.0,
                            'Service', 1)


        # récupère le détail du compte des conversions de devises
        resultat = categorie_plus_frequente('avril', '2022', cursor)

        print("La catégorie la plus fréquente est:", resultat)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_categorie_plus_frequente_null(self):

        print("testing categorie_plus_frequente - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère le détail du compte des conversions de devises
        resultat = categorie_plus_frequente('avril', '2022', cursor)

        print("La catégorie la plus fréquente est:", resultat)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_nb_traductions(self):

        print("testing nb_traductions")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # enregistre 4 factures et les données relatives à leur traduction
        facture_id1 = enregistrer_facture(connection, cursor, '2022-04-11', None,
                                          100.0,'EUR',100.0,
                                          'Service', 1)
        traduction_facture(facture_id1, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')
        facture_id2 = enregistrer_facture(connection, cursor, '2022-04-13', 'Amazon',
                                          150.0, 'EUR', 150.0,
                                          'Travaux', 1)
        traduction_facture(facture_id2, connection, cursor, 'Espagnol', 'Je dis bonjour')
        facture_id3 = enregistrer_facture(connection, cursor, '2022-04-20',
                                          'Le Bon Coin',199.0,
                                          'EUR', 199.0,
                                          'Service', 1)
        traduction_facture(facture_id3, connection, cursor, 'Allemand',
                           'Je dis bonjour')
        facture_id4 = enregistrer_facture(connection, cursor, '2022-07-11', 'Bricorama',
                                          100.0, 'EUR', 100.0,
                                          'Service', 1)
        traduction_facture(facture_id4, connection, cursor, 'Anglais',
                           'Exemple de texte à traduire')

        # récupère le détails de toutes les factures
        details = nb_factures_traduites(None, 2022, cursor)

        print("Nombre de factures traduites sur la période: ", details)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)

    def test_nb_traductions_null(self):

        print("testing nb_traductions - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère le détails de toutes les factures
        details = nb_factures_traduites(None, "2022", cursor)

        print(details)

        # supprime les entrées qui correspondent à des tests
        supprimer_test()
        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_afficher_cat_facture(self):

        print("testing afficher_cat_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère l'ID d'une facture
        facture_id = enregistrer_facture(connection, cursor, '2022-07-11',
                                         'Bricorama',
                                          100.0, 'EUR', 100.0,
                                         'Service', 1)

        # obtient la cat de la facture
        resultat = (afficher_categorie_facture(cursor, facture_id))

        # on affiche le résultat
        print("Catégorie de la facture: ", resultat)

        # on supprime le test de la bdd
        supprimer_test()

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_afficher_cat_facture_null(self):

        print("testing afficher_cat_facture - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # obtient la cat d'une facture imaginaire
        resultat = afficher_categorie_facture(cursor, 999999)

        # on affiche le résultat
        print("Catégorie de la facture: ", resultat)

        # on supprime le test de la bdd
        supprimer_test()

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)



    def test_afficher_date_facture(self):

        print("testing afficher_date_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère l'ID d'une facture
        facture_id = enregistrer_facture(connection, cursor, '2022-07-11',
                                         'Bricorama',
                                          100.0, 'EUR', 100.0,
                                         'Service', 1)

        # récupère la date de la facture
        resultat = afficher_date_facture(cursor, facture_id)

        # on affiche le résultat
        print("Date de la facture: ", resultat)

        # on supprime le test de la bdd
        supprimer_test()

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_afficher_date_facture_null(self):

        print("testing afficher_date_facture - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère la date d'une facture imaginaire
        resultat = afficher_date_facture(cursor, 999999)

        # imprime le résultat
        print("Date de la facture: ", resultat)

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)






    def test_supprimer_facture(self):

        print("testing supprimer_facture")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # récupère l'ID d'une facture
        facture_id = enregistrer_facture(connection, cursor, '2022-07-11',
                                         'Bricorama',100.0, 'EUR',
                                         100.0, 'Service', 1)

        # supprime de la bdd la facture que l'on vient de créer
        supprimer_facture(facture_id, cursor, connection)

        print("Supression de la facture d'ID " + str(facture_id) + " effectuée")

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)


    def test_supprimer_facture_null(self):

        print("testing supprimer_facture - null")

        # récupère la connexion et le curseur
        connection, cursor = connect_to_db()

        # supprime de la bdd une facture imaginaire
        supprimer_facture(999999, cursor, connection)

        # ferme la connexion et le curseur
        fermeture_bdd(connection, cursor)




