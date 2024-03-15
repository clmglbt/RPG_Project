import random
import pickle
import sys
import threading
import time

class Joueur:
    def __init__(self, nom, level=1, xp=0, gold=50, pv=100, strength=10, defense=10, esquive=10, critique=10, nombre_de_mort=0):
        self.nom = nom
        self.level = level
        self.xp = xp
        self.gold = gold
        self.pv = pv
        self.strength = strength
        self.defense = defense
        self.esquive = esquive
        self.critique = critique
        self.nombre_de_mort = nombre_de_mort

        self.level_total = 1
        self.xp_total = 0
        self.gold_total = 50
        self.pv_total = 0
        self.strength_total = 0
        self.defense_total = 0
        self.esquive_total = 0
        self.critique_total = 0
        self.nombre_de_mort = 0


        self.arme_equipee = Couteau()
        
        self.inventaire_armes = []
        self.inventaire_objets = [PotionVie1()]

        self.update_stats()

        self.pv_pool = self.pv_total


    
    def afficher_stats(self):
        print("")
        print("╔══════════ ≪ ❈ ≫ ══════════╗")   
        print(f" Nom : {self.nom}")
        print(f" Niveau : {self.level_total} ({self.xp_total}/{self.levelup_xp()})")
        print(f" HP : [{self.pv_pool}/{self.pv_total}]")
        print(f" Force : {self.strength_total}")
        print(f" Defense : {self.defense_total}")
        print(" ")
        if self.arme_equipee:
            print(f" Arme : {self.arme_equipee.rarity} {self.arme_equipee.nom}")
        else:
            print(" Arme : ")
        print(f" Argent : {self.gold_total}$") 
        print(f" Morts : {self.nombre_de_mort}") 
        print("╚══════════ ≪ ❈ ≫ ══════════╝")
        print("")




    def afficher_inventaire(self):
        print("")
        print("╔══════════════ ≪ ❈ ≫ ══════════════╗")   
        print(" Inventaire")
        print("")
        print(" Armes :")
        for arme in self.inventaire_armes:
            print(f" {arme.rarity} {arme.nom}")
        print("")
        print(" Objets :")
        for objet in self.inventaire_objets:
            print(f" {objet.rarity} {objet.nom}")
        print("╚══════════════ ≪ ❈ ≫ ══════════════╝")
        print("")


    def update_stats(self):

        self.pv_total = int(self.pv * (1.1 ** (self.level_total - 1)))
        self.strength_total = int(self.strength * (1.1 ** (self.level_total - 1)))
        self.defense_total = int(self.defense * (1.1 ** (self.level_total - 1)))
        self.esquive_total = self.esquive
        self.critique_total = self.critique

        if self.arme_equipee:
            self.strength_total += self.arme_equipee.strength
            self.defense_total += self.arme_equipee.defense
            self.esquive_total += self.arme_equipee.esquive
            self.critique_total += self.arme_equipee.critique



    def levelup_xp(self):
        base_xp = 100
        scale_level = 1.5
        xp_required = int(base_xp * (scale_level ** (self.level_total - 1)))
        return xp_required


    def gagner_xp(self, xp_point, gold_recompense):

        self.xp_total += xp_point
        self.gold_total += gold_recompense

        print(f"{self.nom} a gagné {xp_point} points d'expérience et {gold_recompense} gold!")

        while True:
            required_xp = self.levelup_xp()
            if self.xp_total >= required_xp:
                self.level_total += 1
                self.xp_total -= required_xp
                print(f"{self.nom} est monté niveau {self.level_total}!")
                self.pv_pool = int(self.pv_pool + (self.pv_total * 0.1))
                self.update_stats()
            else:
                break


    def attaquer(self, cible):
        degats = self.strength_total - cible.defense
        if degats > 0 and RPG.joueur_chance_critique <= self.critique_total:
            degats = degats * 2
            print(f"COUP CRITIQUE !!! {self.nom} attaque {cible.nom} et lui inflige {degats} points de dégâts.")
            cible.subir_degats(degats)
        elif degats > 0 and RPG.joueur_chance_critique > self.critique_total:
            print(f"{self.nom} attaque {cible.nom} et lui inflige {degats} points de dégâts.")
            cible.subir_degats(degats)
        else:
            print(f"{self.nom} attaque {cible.nom}, mais l'attaque est inefficace.")


    def subir_degats(self, degats):
        self.pv_pool -= degats
        if self.pv_pool <= 0:
            print(f"{self.nom} a été vaincu !")
        else:
            print(f"HP de {self.nom} restants : {self.pv_pool}")




################# MONSTRES ######################

class Cible:
    def __init__(self, nom, pv, strength, defense, esquive, xp_point, gold_recompense):
        self.nom = nom
        self.pv = pv
        self.strength = strength
        self.defense = defense
        self.esquive = esquive
        self.xp_point = xp_point
        self.gold_recompense = gold_recompense


    def attaquer(self, attaquant):
        degats = int(self.strength - (self.strength * (attaquant.defense_total/100)))
        if degats > 0 and RPG.joueur_chance_esquive <= attaquant.esquive_total :
            print(f"{self.nom} attaque {attaquant.nom} mais {attaquant.nom} évite l'attaque.")
        elif degats > 0 and RPG.joueur_chance_esquive > attaquant.esquive_total :
            print(f"{self.nom} attaque {attaquant.nom} et lui inflige {degats} points de dégâts.")
            attaquant.subir_degats(degats)
        else:
            print(f"{self.nom} attaque {attaquant.nom}, mais l'attaque est inefficace.")


    def subir_degats(self, degats):
        self.pv -= degats
        if self.pv <= 0:
            print(f"{self.nom} a été vaincu !")
        else:
            print(f"HP de {self.nom} restants : {self.pv}")



class Slime(Cible):
    def __init__(self, nom="Slime", pv=40, strength=7, defense=0, esquive=5, xp_point=25, niveau=1, gold_recompense=10):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Gobelin(Cible):
    def __init__(self, nom="Gobelin", pv=80, strength=12, defense=0, esquive=10, xp_point=50, niveau=2, gold_recompense=25):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Brigand(Cible):
    def __init__(self, nom="Brigand", pv=100, strength=15, defense=3, esquive=10, xp_point=100, niveau=5, gold_recompense=60):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Troll(Cible):
    def __init__(self, nom="Troll", pv=160, strength=20, defense=0, esquive=15, xp_point=250, niveau=8, gold_recompense=40):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Zombie(Cible):
    def __init__(self, nom="Zombie", pv=120, strength=15, defense=5, esquive=0, xp_point=300, niveau=7, gold_recompense=30):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Diable(Cible):
    def __init__(self, nom="Diable", pv=170, strength=20, defense=10, esquive=15, xp_point=500, niveau=12, gold_recompense=60):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Ogre(Cible):
    def __init__(self, nom="Ogre", pv=250, strength=25, defense=10, esquive=5, xp_point=750, niveau=25, gold_recompense=150):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Golem(Cible):
    def __init__(self, nom="Golem des Forêts", pv=300, strength=30, defense=20, esquive=0, xp_point=1500, niveau=50, gold_recompense=300):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau


class Dragon(Cible):
    def __init__(self, nom="Dragon", pv=1000, strength=50, defense=20, esquive=0, xp_point=5000, niveau=100, gold_recompense=1000):
        super().__init__(nom, pv, strength, defense, esquive, xp_point, gold_recompense)
        self.niveau = niveau




############################### ARMES ################################
        

class Arme:
    def __init__(self, nom, rarity, description, strength, defense, critique, esquive, prix_de_vente):
        self.nom = nom
        self.rarity = rarity
        self.description = description
        self.strength = strength
        self.defense = defense
        self.esquive = esquive
        self.critique = critique 
        self.prix_de_vente = prix_de_vente

class Couteau(Arme):
    def __init__(self, nom="Couteau", rarity="[COMMUN]", description="Une petite lame émoussée.\n Force = 2", 
                 strength=2, defense=0, esquive=0, critique=0, prix_de_vente=5):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class EpeeBois(Arme):
    def __init__(self, nom="Epee en bois", rarity="[COMMUN]", description="Une épée simple mais solide.\n Force = 5\n Defense = 2", 
                 strength=5, defense=2, esquive=0, critique=0, prix_de_vente=15):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class Dagues_(Arme):
    def __init__(self, nom="Dagues", rarity="[COMMUN]", description="Des petites épées. Pas très puissantes mais permettent de se mouvoir facilement.\n Force = 5\n Esquive = 10%\n Chance de critique = 5%", 
                 strength=500, defense=0, esquive=10, critique=5, prix_de_vente=30):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)
        

class Massue(Arme):
    def __init__(self, nom="Massue en pierre", rarity="[COMMUN]", description="Un gros bâton avec un rocher accroché au bout. Puissant mais dur à manier.\n Force = 12\n Defense = 5\n Esquive = -5", 
                 strength=12, defense=5, esquive=-5, critique=0, prix_de_vente=20):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class EpeeFer(Arme):
    def __init__(self, nom="Epee en acier", rarity="[RARE]", description="Une belle arme forgée par un artisan de qualité.\n Force = 17\n Defense = 5\n Chance de critique = 2%", 
                 strength=17, defense=5, esquive=0, critique=2, prix_de_vente=100):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)
        

class Bouclier(Arme):
    def __init__(self, nom="Bouclier à pointes", rarity="[RARE]", description="Une arme qui permet aussi bien de se défendre que d'attaquer.\n Force = 8 \n Defense = 15", 
                 strength=8, defense=15, esquive=0, critique=0, prix_de_vente=80):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class Chaines(Arme):
    def __init__(self, nom="Chaînes", rarity="[RARE]", description="Des chaines en acier avec un poids au bout.\n Force = 13\n Defense = 2\n Esquive = 10%", 
                 strength=13, defense=2, esquive=10, critique=0, prix_de_vente=90):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class Excalibur_(Arme):
    def __init__(self, nom="Excalibur", rarity="[LEGENDAIRE]", description="Une épée légendaire maniée par les plus grands guerriers.\n Force = 30\n Defense = 10\n Esquive = 5%\n Chance de critique = 15%", 
                 strength=30, defense=10, esquive=5, critique=15, prix_de_vente=400):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class Tronconneuse_(Arme):
    def __init__(self, nom="Tronconneuse", rarity="[LEGENDAIRE]", description="Une grande lame capable de déchiqueter n'importe quoi.\n Force = 25\n Defense = 0\n Esquive = -5%\n Chance de critique = 50%", 
                 strength=25, defense=0, esquive=-5, critique=50, prix_de_vente=300):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class SabreNinja(Arme):
    def __init__(self, nom="Sabre des ombres", rarity="[LEGENDAIRE]", description="Le maitre ninja à qui appartenait ce sabre était réputé pour être aussi rapide que le son.\n Force = 24\n Defense = 5\n Esquive = 50%\n Chance de critique = 10%", 
                 strength=24, defense=5, esquive=50, critique=10, prix_de_vente=350):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)


class LameDragon(Arme):
    def __init__(self, nom="Lame du Dragon", rarity="[MYTHIQUE]", description="Ce trésor légendaire gardé par le Dragon prouve que vous en êtes venu a bout. Félicitations!\n Force = 50\n Defense = 15\n Chance de critique = 25%", 
                 strength=50, defense=15, esquive=0, critique=25, prix_de_vente=2000):
        super().__init__(nom, rarity, description, strength, defense, esquive, critique, prix_de_vente)




##################################### POTIONS #####################################
        
class Objet:
    def __init__(self, nom, rarity, description, pv, strength, defense, prix_de_vente):
        self.nom = nom
        self.rarity = rarity
        self.description = description
        self.pv = pv
        self.strength = strength
        self.defense = defense
        self.prix_de_vente = prix_de_vente

class PotionVie1(Objet):
    def __init__(self, nom="Petite Potion de Vie", rarity="[COMMUN]", description="Restaure 50'%' des pv manquants", pv=50, strength=0, defense=0, prix_de_vente=15):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)

class PotionVie2(Objet):
    def __init__(self, nom="Grande Potion de Vie", rarity="[RARE]", description="Restaure 100'%' des pv manquants", pv=100, strength=0, defense=0, prix_de_vente=25):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)


class PotionForce1(Objet):
    def __init__(self, nom="Petite Potion de Force", rarity="[COMMUN]", description="Multiplie la force par 1.5x jusqu'à la fin du combat", pv=0, strength=0.5, defense=0, prix_de_vente=20):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)
        
class PotionForce2(Objet):
    def __init__(self, nom="Grande Potion de Force", rarity="[RARE]", description="Multiplie la force par 2x jusqu'à la fin du combat", pv=0, strength=1, defense=0, prix_de_vente=45):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)


class PotionResistance1(Objet):
    def __init__(self, nom="Petite Potion de Resistance", rarity="[COMMUN]", description="Multiplie la defense par 1.5x jusqu'à la fin du combat", pv=0, strength=0, defense=0.5, prix_de_vente=15):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)

class PotionResistance2(Objet):
    def __init__(self, nom="Grande Potion de Resistance", rarity="[RARE]", description="Multiplie la defense par 2x jusqu'à la fin du combat", pv=0, strength=0, defense=1, prix_de_vente=30):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)


class PotionUltime(Objet):
    def __init__(self, nom="Potion Ultime", rarity="[LEGENDAIRE]", description="Soigne les pv et augmente toute les statistiques jusqu'à la fin du combat", pv=100, strength=1, defense=1, prix_de_vente=200):
                super().__init__(nom, rarity, description, pv, strength, defense, prix_de_vente)






################################# JEU #####################################



class RPG:
    
    joueur_chance_esquive = random.randint(1, 100)
    joueur_chance_critique = random.randint(1,100)
    
    def generer_ennemi_1(self):
        proba_spawn_monstre_1 = random.randint(1, 100)
        if proba_spawn_monstre_1 < 40:
            return Slime()
        if proba_spawn_monstre_1 >= 40 and proba_spawn_monstre_1 < 75:
            return Gobelin()
        if proba_spawn_monstre_1 >= 75 and proba_spawn_monstre_1 < 92:
            return Brigand()
        else :
            return Troll()

    def generer_ennemi_2(self):
        proba_spawn_monstre_2 = random.randint(1, 100)
        if proba_spawn_monstre_2 < 40:
            return Zombie()
        if proba_spawn_monstre_2 >= 40 and proba_spawn_monstre_2 < 75:
            return Diable()
        if proba_spawn_monstre_2 >= 75 and proba_spawn_monstre_2 < 92:
            return Ogre()
        else :
            return Golem()
        


########## INVENTAIRE ##########
        

    def menu_inventaire(self, joueur):
        inventaire_true = 1
        while inventaire_true == 1:
            joueur.afficher_inventaire()
            time.sleep(1)
            print("╔═════════════ ≪ ❈ ≫ ═════════════╗")
            print(" 1. Afficher les infos d'un item.")
            print(" 2. Equiper une arme.")
            print(" 3. Desequiper l'arme équipée.")
            print(" 4. Quitter.")
            print("╚═════════════ ≪ ❈ ≫ ═════════════╝")
            print("")
            choix_inventaire = int(input(""))
            time.sleep(1)




            if choix_inventaire == 1:
                item_trouve = None

                nom_item = input("Donnez le nom de l'item que vous souhaitez inspecter. ")
                time.sleep(1)

                for arme in joueur.inventaire_armes:
                    for objet in joueur.inventaire_objets:    
                        if arme.nom.lower() == nom_item.lower():
                            item_trouve = arme
                            break
                        if objet.nom.lower() == nom_item.lower():
                            item_trouve = objet
                            break       

                if item_trouve:
                    print("")
                    print(f"{item_trouve.rarity} {item_trouve.nom}:")
                    print(f"{item_trouve.description}")
                    print("")
                    item_trouve = None
                    time.sleep(1)
                
                else:
                    print("")
                    print(f"Vous ne possédez pas cet objet. Vérifiez l'orthographe.")
                    print("")




            elif choix_inventaire == 2 :
                choix_arme = None

                print("")
                choix_arme = input("Choisissez le nom de l'arme que vous souhaitez équiper. ")
                for arme in joueur.inventaire_armes:
                    if arme.nom.lower() == choix_arme.lower():
                        choix_arme = arme
                        break
                    
                if choix_arme:
                    print("")
                    if joueur.arme_equipee:
                        joueur.inventaire_armes.append(joueur.arme_equipee)
                        print(f"Vous avez déséquipé {joueur.arme_equipee.rarity} {joueur.arme_equipee.nom}")
                    joueur.arme_equipee = choix_arme
                    joueur.inventaire_armes.remove(choix_arme)
                    print(f"Vous avez équipé {choix_arme.rarity} {choix_arme.nom}")
                    print("")
                    joueur.update_stats()
                
                else:
                    print("")
                    print(f"Vous ne possédez pas cet objet. Vérifiez l'orthographe.")
                    print("")



            elif choix_inventaire == 3:

                print("")
                if joueur.arme_equipee:
                    arme_desequipee = joueur.arme_equipee
                    joueur.inventaire_armes.append(arme_desequipee)
                    joueur.arme_equipee = None
                    print(f"Vous avez déséquipé {arme_desequipee.rarity} {arme_desequipee.nom}")
                    print("")
                    joueur.update_stats()
                else:
                    print("")
                    print("Vous n'avez pas d'arme équipée.")
                    print("")


            
            elif choix_inventaire == 4:
                inventaire_true = 0
                return
            
            else:
                print("Choix invalide.")






    

########## MENU DE JEU ################

    def menu(self, joueur):

        joueur.pv_pool = joueur.pv_total


        print("")
        print("╔══════════ ≪ ❈ ≫ ══════════╗") 
        print(" Choisissez une action.")
        print("")
        print(" 1. Profil")
        print(" 2. Inventaire")
        print(" 3. Aventure")
        print(" 4. Sauvegarder et Quitter")
        print(" 5. Infos")
        print("╚══════════ ≪ ❈ ≫ ══════════╝")
        print("")
        choix_menu = int(input(""))


        if choix_menu == 1:
            joueur.afficher_stats()
            time.sleep(1)
            return self.menu(joueur)


        elif choix_menu == 2:
            self.menu_inventaire(joueur)
            return self.menu(joueur)
            

        elif choix_menu == 3:
            self.aventure_init(joueur)
            
        
        elif choix_menu == 4:
            self.sauvegarder(joueur)
            sys.exit()



        elif choix_menu == 5:
            print("")
            print("╔══════════ ≪ ❈ ≫ ══════════╗")
            print(" Ce RPG a été codé par :")
            print("")
            print(" Lucien BENOIST")
            print(" Clément GILBERT")
            print("")
            print(" Contactez nous sur Discord")
            print(" @bambiiception")
            print(" @clmnocap")
            print("╚══════════ ≪ ❈ ≫ ══════════╝")
            print("")

            time.sleep(2)
            return self.menu(joueur)
        




    
########### COMBAT ################

    def combat(self, joueur, ennemi):
        print(f"Vous rencontrez un LVL[{ennemi.niveau}] {ennemi.nom}.")

        while joueur.pv > 0 and ennemi.pv > 0:
            time.sleep(1)
            RPG.joueur_chance_esquive = random.randint(1, 100)
            RPG.joueur_chance_critique = random.randint(1,100)

            print("")
            print("╔══════════ ≪ ❈ ≫ ══════════╗")
            print(" Choisissez une action.")
            print("")
            print(" 1. Combat")
            print(" 2. Objet")
            print(" 3. Observer")
            print(" 4. Fuir")
            print("╚══════════ ≪ ❈ ≫ ══════════╝")
            print("")
            choix_combat = int(input(""))
            time.sleep(1)

            if choix_combat == 1:
                joueur.attaquer(ennemi)
                time.sleep(1)

                if ennemi.pv <= 0:
                    print("Vous avez vaincu l'ennemi !")
                    joueur.gagner_xp(ennemi.xp_point, ennemi.gold_recompense)
                    joueur.update_stats()
                    return
                
                else:
                    ennemi.attaquer(joueur) 
                    if joueur.pv <= 0:
                        print("Vous avez été vaincu !")
                        time.sleep(1)
                        print(f"Pendant qu'il était évanoui, les monstres ont volé {int(joueur.gold_total/2)}$ a {joueur.nom}...")
                        joueur.gold_total = int(joueur.gold_total/2)
                        time.sleep(1)
                        joueur.nombre_de_mort_total = joueur.nombre_de_mort_total + 1
                        print(f"Vous êtes mort un total de {joueur.nombre_de_mort_total} fois.")
                        time.sleep(2)
                        print("Ne perdez pas espoir!")
                        time.sleep(1)
                        print("Recommencez une aventure afin de devenir encore plus puissant.")
                        time.sleep(1)
                        return self.menu(joueur)
                        
            elif choix_combat == 2:
                print("")
                print("╔═════════════ ≪ ❈ ≫ ═════════════╗")
                print(" Liste des objets")
                print("")
                for objet in joueur.inventaire_objets:
                    print(f" {objet.rarity} {objet.nom}")
                print("╚═════════════ ≪ ❈ ≫ ═════════════╝")
                print("")
                choix_combat_objet_quitter = int(input("Que souhaitez vous faire?\n\n"
                                                       "1. Utiliser un objet\n"
                                                       "2. Retour\n"
                                                       ""))
                if choix_combat_objet_quitter == 1:
                    choix_objet = input("Ecrivez le nom de l'objet que vous souhaitez utiliser.\n"
                                        "")
                    
                    for objet in joueur.inventaire_objets:
                        if objet.nom.lower() == choix_objet.lower():
                            choix_objet = objet
                            break
                        
                    if choix_objet:

                        joueur.inventaire_objets.remove(choix_objet)

                        pv_regen_objet = int(objet.pv/100 * joueur.pv_total)
                        joueur.pv_pool = joueur.pv_pool + pv_regen_objet
                        if joueur.pv_pool > joueur.pv_total:
                            joueur.pv_pool = joueur.pv_total
                        
                        force_bonus_objet = int(joueur.strength_total * objet.strength)
                        joueur.strength_total =+ force_bonus_objet

                        defense_bonus_objet = int(joueur.defense_total * objet.defense)
                        joueur.defense_total =+ defense_bonus_objet

                        print("")
                        print(f"Vous avez utilisé {choix_objet.rarity} {choix_objet.nom}.")

                        if choix_objet == PotionVie1() or choix_objet == PotionVie2():
                            print(f"{joueur.nom} se soigne pour un total de {pv_regen_objet} PV. Vous avez désormais {joueur.pv_pool} PV.")

                        if choix_objet == PotionForce1() or choix_objet == PotionForce2():
                            print(f"La force de {joueur.nom} augmente de {force_bonus_objet}.")
                        
                        if choix_objet == PotionResistance1() or choix_objet == PotionResistance2():
                            print(f"La defense de {joueur.nom} augmente de {defense_bonus_objet}.")
                        
                        if choix_objet == PotionUltime():
                            print(f"{joueur.nom} se soigne de {pv_regen_objet}, sa force augmente de {force_bonus_objet} et sa defense de {defense_bonus_objet}.")


                        time.sleep(1)
                        ennemi.attaquer(joueur) 
                        if joueur.pv <= 0:
                            print("Vous avez été vaincu !")
                            time.sleep(1)
                            print(f"Pendant qu'il était évanoui, les monstres ont volé {int(joueur.gold_total/2)}$ a {joueur.nom}...")
                            joueur.gold_total = int(joueur.gold_total/2)
                            time.sleep(1)
                            joueur.nombre_de_mort_total = joueur.nombre_de_mort_total + 1
                            print(f"Vous êtes mort un total de {joueur.nombre_de_mort_total} fois.")
                            time.sleep(2)
                            print("Ne perdez pas espoir!")
                            time.sleep(1)
                            print("Recommencez une aventure afin de devenir encore plus puissant.")
                            return self.menu(joueur)


                    else:
                        print("")
                        print(f"Vous ne possédez pas cet objet. Vérifiez l'orthographe.")
                        print("")

                
                
            elif choix_combat == 3:
                print("")
                print("╔═════════════ ≪ ❈ ≫ ═════════════╗")
                print(f" {ennemi.nom} LVL[{ennemi.niveau}]\n"
                      f" PV : {ennemi.pv}\n"
                      f" Force : {ennemi.strength}\n"
                      f" Defense : {ennemi.defense}")
                print("╚═════════════ ≪ ❈ ≫ ═════════════╝")
                print("")
                
                
            elif choix_combat == 4:
                self.win_or_lose_fuite = 0
                if ennemi == Dragon():
                    print("[DRAGON] CERTAINEMENT PAS! RESTE ICI ET BATS TOI.")
                    ennemi.attaquer(joueur)
                    if joueur.pv <= 0:
                        print("Vous avez été vaincu !")
                        time.sleep(1)
                        print(f"Pendant qu'il était évanoui, les monstres ont volé {int(joueur.gold_total/2)}$ a {joueur.nom}...")
                        joueur.gold_total = int(joueur.gold_total/2)
                        time.sleep(1)
                        joueur.nombre_de_mort_total = joueur.nombre_de_mort_total + 1
                        print(f"Vous êtes mort un total de {joueur.nombre_de_mort_total} fois.")
                        time.sleep(2)
                        print("Ne perdez pas espoir!")
                        time.sleep(1)
                        print("Recommencez une aventure afin de devenir encore plus puissant.")
                        return self.menu(joueur)
                    
                else:
                    self.fuite(joueur, ennemi)
                    if self.win_or_lose_fuite == 1:
                        break
                
            else:
                print("Votre choix n'est pas valide. Réessayez.")
    



############## FUITE #############
                

    def fuite(self, joueur, ennemi):

        reponse_fuite = 0

        facteur_1 = random.randint(1, 10)
        facteur_2 = random.randint(1, 10)
        facteur_3 = random.randint(1, 20)

        resultat_fuite = (facteur_1 * facteur_2 + facteur_3)

        time.sleep(1)
        print(f"[{ennemi.nom}] Oho, tu souhaites t'échapper?")
        time.sleep(1)
        print(f"[{ennemi.nom}] Dans ce cas là, réponds à ce calcul mental !")
        time.sleep(1)
        print(f"[{ennemi.nom}] Attention, ton temps est limité !")
        time.sleep(1)
        print(f"[{ennemi.nom}] Bonne chance... je vais compter...")
        time.sleep(2)
        print(f"[{ennemi.nom}] 3...")
        time.sleep(1)
        print(f"[{ennemi.nom}] 2...")
        time.sleep(1)
        print(f"[{ennemi.nom}] 1...")
        time.sleep(1)
        print(f"[{ennemi.nom}] Combien font : {facteur_1} x {facteur_2} + {facteur_3}")

        def attendre_reponse():
            nonlocal reponse_fuite
            reponse_fuite = int(input("Réponse : "))
        
        thread_attente = threading.Thread(target=attendre_reponse)

        thread_attente.start()
        thread_attente.join(timeout=8)

        if reponse_fuite is not None:
            time.sleep(1)
            print(f"Vous avez répondu : {reponse_fuite}")
            time.sleep(1)
            print(f"[{ennemi.nom}] La réponse était... {resultat_fuite} !")
            time.sleep(2)
            print(f"[{ennemi.nom}] ...")
            time.sleep(1)
            
            if reponse_fuite == resultat_fuite:
                print(f"[{ennemi.nom}] Hmmm... Bien joué.")
                time.sleep(1)
                print(f"[{ennemi.nom}] Tu peux partir... pour cette fois.")
                time.sleep(1)
                self.win_or_lose_fuite = 1

            else:
                print(f"[{ennemi.nom}] Raté! Prends ça!")
                time.sleep(1)
                ennemi.attaquer(joueur)
                if joueur.pv <= 0:
                    print("Vous avez été vaincu !")
                    time.sleep(1)
                    print(f"Pendant qu'il était évanoui, les monstres ont volé {int(joueur.gold_total/2)}$ a {joueur.nom}...")
                    joueur.gold_total = int(joueur.gold_total/2)
                    time.sleep(1)
                    joueur.nombre_de_mort_total = joueur.nombre_de_mort_total + 1
                    print(f"Vous êtes mort un total de {joueur.nombre_de_mort_total} fois.")
                    time.sleep(2)
                    print("Ne perdez pas espoir!")
                    time.sleep(1)
                    print("Recommencez une aventure afin de devenir encore plus puissant.")
                    return self.menu(joueur)
                    
                

        else:
            print(f"[{ennemi.nom}] Temps écoulé! Prends ça! Mouahahaha...")
            time.sleep(1)
            ennemi.attaquer(joueur)
            if joueur.pv <= 0:
                print("Vous avez été vaincu !")
                time.sleep(1)
                print(f"Pendant qu'il était évanoui, les monstres ont volé {int(joueur.gold_total/2)}$ a {joueur.nom}...")
                joueur.gold_total = int(joueur.gold_total/2)
                time.sleep(2)
                print("Ne perdez pas espoir!")
                time.sleep(1)
                print("Recommencez une aventure afin de devenir encore plus puissant.")
                return self.menu(joueur)






################ LOOT TABLE ##################
    
    def recompense_loot(self, joueur):
        
        chance_loot = random.randint(1, 100)
        drop_loot = None

        print("Vous ouvrez un coffre!")
        time.sleep(1)
        print(".")
        time.sleep(1)
        print("..")
        time.sleep(1)
        print("...")
        time.sleep(1)

        if chance_loot >= 92:
            drop_loot = random.choice([Excalibur_(), Tronconneuse_(), SabreNinja(), PotionUltime()])
            print(f"INCROYABLE!!! Vous avez obtenu {drop_loot.rarity} {drop_loot.nom}.")

            if isinstance(drop_loot, PotionUltime):
                joueur.inventaire_objets.append(drop_loot)
            else:
                joueur.inventaire_armes.append(drop_loot)


        if chance_loot < 92 and chance_loot > 72 :
            drop_loot = random.choice([Chaines(), EpeeFer(), Bouclier(), PotionVie2(), PotionForce2(), PotionResistance2()])
            print(f"Wow! Vous avez obtenu {drop_loot.rarity} {drop_loot.nom}.")

            if isinstance(drop_loot, (PotionVie2, PotionForce2, PotionResistance2)):
                joueur.inventaire_objets.append(drop_loot)
            else:
                joueur.inventaire_armes.append(drop_loot)


        if chance_loot <= 72 :
            drop_loot = random.choice([EpeeBois(), Massue(), Dagues_(), PotionVie1(), PotionForce1(), PotionResistance1()])
            print(f"Vous avez obtenu {drop_loot.rarity} {drop_loot.nom}.")

            if isinstance(drop_loot, (PotionVie1, PotionForce1, PotionResistance1)):
                joueur.inventaire_objets.append(drop_loot)
            else:
                joueur.inventaire_armes.append(drop_loot)



######### LOOT PIEGE ##############

    def loot_piege(self, joueur):

        print("Vous ouvrez un coffre!")
        time.sleep(1)
        print(".")
        time.sleep(1)
        print("..")
        time.sleep(1)
        print("...")
        time.sleep(1)
        print("OUCH! Le coffre explose et vous inflige des dégats.")
        time.sleep(1)

        degats_coffre_piege = int(joueur.pv_total / 2)

        joueur.pv_pool = int(joueur.pv_pool - degats_coffre_piege)
        if joueur.pv_pool <= 0:
            joueur.pv_pool = 1

        print("")
        print(f"{joueur.nom} subit {degats_coffre_piege} dégats. PV restants: {joueur.pv_pool}")
        print("")




################# FONTAINE DES FEES ####################

    def fontaine(self, joueur):

        proba_gain_fontaine = random.randint(1, 2)

        print("Vous pouvez choisir de faire un don aux fées.")
        time.sleep(1)
        print("")
        print("╔════════════ ≪ ❈ ≫ ════════════╗")
        print(" Souhaitez-vous mettre")
        print(" de l'argent dans la fontaine?")
        print(f"(Vous possédez {joueur.gold_total}$.)")
        print("")
        print(" 1. Oui")
        print(" 2. Non")
        print("╚════════════ ≪ ❈ ≫ ════════════╝")
        print("")
        choix_fontaine = int(input(""))
        time.sleep(1)

        if choix_fontaine == 1:
            print("")
            print("Combien souhaitez-vous donner?")
            print("")
            choix_fontaine_don = int(input(""))
            time.sleep(1)
                
            if choix_fontaine_don > joueur.gold_total:
                print("")
                print("Vous n'avez pas assez d'argent. Vous sentez un regard désapprobateur sur vous.")
                time.sleep(1)
                print("")
                return self.fontaine(joueur)

            else:
                print(f"Vous jetez {choix_fontaine_don}$ dans la fontaine.")
                joueur.gold_total = joueur.gold_total - choix_fontaine_don
                time.sleep(1)
                print("...")
                time.sleep(2)

                if proba_gain_fontaine == 1:
                    gain_fontaine = choix_fontaine_don * 2
                    print("Les fées ont reconnu votre générosité.")
                    time.sleep(1)
                    print(f"Vous recevez {gain_fontaine}$ !")
                    joueur.gold_total = joueur.gold_total + gain_fontaine
                    time.sleep(1)

                if proba_gain_fontaine == 2:
                    print("Mais rien ne se passe...")

        elif choix_fontaine == 2:
            print("")
            print("Vous décidez de partir...")
            time.sleep(1)

        else:
            print("Choix invalide. Reéssayez")
            return self.fontaine(joueur)




################ MAISON DE REPOS ####################


    def maison_repos(self, joueur):
        time.sleep(1)
        print("Vous arrivez devant une maison abandonnée.")
        time.sleep(1)
        print("")
        print("╔══════════════ ≪ ❈ ≫ ══════════════╗")
        print(" Souhaitez vous vous reposer un peu?")
        print("")
        print(" 1. Oui")
        print(" 2. Non")
        print("╚══════════════ ≪ ❈ ≫ ══════════════╝")
        print("")
        choix_maison_repos = int(input(""))
        time.sleep(1)

        if choix_maison_repos == 1:
            joueur.pv_pool = joueur.pv_total
            print("Vous vous reposez quelques temps et restaurez toute votre énergie.")
            print(f"Les PV de {joueur.nom} sont désormais de {joueur.pv_pool} !")

        elif choix_maison_repos == 2:
            print("Pourquoi refuser un petit somme? Comme vous le souhaitez...")

        else:
            print("Choix invalide. Réessayez.")
            return self.maison_repos(joueur)




################ EVENT BOSS #####################
        
    def event_boss(self, joueur):

        time.sleep(1)
        print("Vous pénétrez dans l'antre du Dragon...")
        time.sleep(2)
        print("...")
        time.sleep(1)
        print("Soudain la terre tremble et un grand réptile surgit du fond de la grotte.")
        print(" Le Dragon se dresse devant vous!")
        time.sleep(1)
        print("[DRAGON] QUI OSE S'INTRODUIRE CHEZ MOI?")
        time.sleep(2)
        print("[DRAGON] ...")
        time.sleep(2)
        print(f"[DRAGON] OH, C'EST TOI, {joueur.nom}. ON M'A PARLE DE TOI.")
        time.sleep(1)
        print("[DRAGON] TU SOUHAITAIS ME VAINCRE APPAREMMENT? VOILA QUI EST AMUSANT.")
        time.sleep(1)
        print("[DRAGON] VOYONS VOIR DE QUOI TU ES CAPABLE. EN GARDE !")
        time.sleep(2)

        ennemi = Dragon()

        self.combat(joueur, ennemi)

        self.case_nombre = 0

        if joueur.pv_pool > 0 :
            time.sleep(2)
            print("[DRAGON] C'EST IMPOSSIBLE... J'AI ETE VAINCU?")
            time.sleep(1)
            print("[DRAGON] MOUAHAHAHA.. FELICITATIONS PETIT HOMME !!")
            print("[DRAGON] J'ACCEPTE MA DEFAITE. PRENDS CECI EN RECOMPENSE.")
            time.sleep(2)

            joueur.inventaire_armes.append(LameDragon())
            print("")
            print(f"{joueur.nom} a obtenu [MYTHIQUE] Lame du Dragon !!")
            print("")
            time.sleep(3)

            print("Félicitations!! Bien que l'objectif du jeu soit atteint, libre à vous de recommencer autant d'aventures que vous souhaitez.")
            time.sleep(2)
            print("Ce jeu a été réalisé dans le cadre d'un projet pour l'HETIC.")
            time.sleep(2)
            print("Crédits et remerciements : Lucien et Clement pour la création du jeu,  Kylian et Robin pour l'aide précieuse apportée.")
            time.sleep(2)
            print("Merci d'avoir joué!")
            time.sleep(2)

            return self.menu(joueur)







############ SHOP ###################

    def shop(self, joueur):

        print("[VENDEUR] Bienvenue dans la boutique!")
        print(f"(Argent : {joueur.gold_total}$)")
        time.sleep(1)
        print("")
        print("╔══════════ ≪ ❈ ≫ ══════════╗")   
        print(" Que souhaitez vous faire?")
        print("")
        print(" 1. Acheter")
        print(" 2. Vendre")
        print(" 3. Quitter")
        print("╚══════════ ≪ ❈ ≫ ══════════╝")
        print("")

        choix_shop = int(input(""))
        time.sleep(1)

        if choix_shop == 1:
            print("")
            print("╔══════════ ≪ ❈ ≫ ══════════╗")
            print(" Que souhaitez-vous acheter? ")
            print("")
            print(" 1. Coffre d'objets  -  100$")
            print(" 2. Soin complet  -  50$")
            print("")
            print(" 3. Retour")
            print("╚══════════ ≪ ❈ ≫ ══════════╝")
            print("")
            choix_shop_achat = int(input(""))

            if choix_shop_achat == 1:
                time.sleep(1)

                if joueur.gold_total >= 100:
                    print("Vous avez acheté un coffre d'objets. (-100$)")
                    time.sleep(1)
                    print(f"[VENDEUR] Je me demande ce que ça contient.")
                    joueur.gold_total = joueur.gold_total - 100
                    time.sleep(1)
                    self.recompense_loot(joueur)
                    time.sleep(1)
                    return self.shop(joueur)
                
                else:
                    print("[VENDEUR] Vous n'avez pas d'argent pour acheter cela.")
                    time.sleep(1)
                    return self.shop(joueur)
                
            
            elif choix_shop_achat == 2:
                time.sleep(1)

                if joueur.gold_total >= 50:
                    print("Vous vous reposez dans l'arrière boutique et récupérez tout vos PV. (-50$)")
                    time.sleep(1)
                    print(f"[VENDEUR] Alors {joueur.nom}, bien dormi?")
                    joueur.gold_total = joueur.gold_total - 50
                    time.sleep(1)
                    joueur.pv_pool = joueur.pv_total
                    time.sleep(1)
                    return self.shop(joueur)
                
                else:
                    print("[VENDEUR] Vous n'avez pas d'argent pour acheter cela.")
                    time.sleep(1)
                    return self.shop(joueur)


            elif choix_shop_achat == 3:
                time.sleep(1)
                return self.shop(joueur)
            

            else:
                time.sleep(1)
                print("Votre choix est invalide. Reéssayez.")
                return self.shop(joueur)
        

        elif choix_shop == 2:
            
            while True :
                print("╔═══════════════════ ≪ ❈ ≫ ═══════════════════╗")
                print(" Inventaire :")
                print("")
                print(" Armes :")
                for arme in joueur.inventaire_armes:
                    print(f" {arme.prix_de_vente}$  -  {arme.rarity} {arme.nom}")
                print("")
                print(" Objets :")
                for objet in joueur.inventaire_objets:
                    print(f" {objet.prix_de_vente}$  -  {objet.rarity} {objet.nom}")
                print("╚═══════════════════ ≪ ❈ ≫ ═══════════════════╝")
                print("")

                time.sleep(1)
                print("╔══════════ ≪ ❈ ≫ ══════════╗")
                print(" Que souhaitez vous faire?")
                print("")
                print(" 1. Vendre une arme")
                print(" 2. Vendre un objet")
                print(" 3. Annuler")
                print("╚══════════ ≪ ❈ ≫ ══════════╝")
                print("")
                choix_shop_vente = int(input(""))


                if choix_shop_vente == 1:

                    item_trouve = None

                    nom_item = input("Donnez le nom de l'arme que vous souhaitez vendre. ")
                    time.sleep(1)

                    for arme in joueur.inventaire_armes:
                        if arme.nom.lower() == nom_item.lower():
                            item_trouve = arme
                            break

                    if item_trouve:
                        joueur.inventaire_armes.remove(item_trouve)
                        joueur.gold_total = joueur.gold_total + item_trouve.prix_de_vente
                        print(f"Vous avez vendu {item_trouve.rarity} {item_trouve.nom} pour {item_trouve.prix_de_vente}$.")
                        print(f"Vous avez désormais un total de {joueur.gold_total}$")
                        time.sleep(1)
                        print(f"[VENDEUR] Merci bien, {joueur.nom} !")
                        return self.shop(joueur)


                elif choix_shop_vente == 2:

                    item_trouve = None

                    nom_item = input("Donnez le nom de l'objet que vous souhaitez vendre. ")
                    time.sleep(1)

                    for objet in joueur.inventaire_objets:
                        if objet.nom.lower() == nom_item.lower():
                            item_trouve = objet
                            break                      

                    if item_trouve:
                        joueur.inventaire_objets.remove(item_trouve)
                        joueur.gold_total = joueur.gold_total + item_trouve.prix_de_vente
                        print(f"Vous avez vendu {item_trouve.rarity} {item_trouve.nom} pour {item_trouve.prix_de_vente}$.")
                        print(f"Vous avez désormais un total de {joueur.gold_total}$")
                        time.sleep(1)
                        print(f"[VENDEUR] Merci bien, {joueur.nom} !")
                        return self.shop(joueur)


                elif choix_shop_vente == 3:
                    return self.shop(joueur)

                else:
                    print("Choix invalide.")
                    return self.shop(joueur)
                            
            

        elif choix_shop == 3:
            print("")
            print("Vous quittez le magasin.")
            time.sleep(1)
            print(f"[VENDEUR] A la revoyure, {joueur.nom} !")
            print("")

        
        else:
            print("Choix invalide. Réessayez.")
            return self.shop(joueur)  
                
            

    def salle_des_coffres(self, joueur):
        time.sleep(1)
        chance_coffre_piege = random.randint(1, 4)
        print("Vous apercevez un coffre au milieu d'une prairie...")
        time.sleep(1)
        print("")
        print("╔══════════ ≪ ❈ ≫ ══════════╗")
        print(" C'est peut être un piège.")
        print(" Que souhaitez-faire?")
        print("")
        print(" 1. Ouvrir")
        print(" 2. Partir")
        print("╚══════════ ≪ ❈ ≫ ══════════╝")
        print("")
        choix_coffre_ouvrir = int(input(""))

        if choix_coffre_ouvrir == 1:
            if chance_coffre_piege == 1:
                self.loot_piege(joueur)

            else:
                self.recompense_loot(joueur)
            
        elif choix_coffre_ouvrir == 2:
            time.sleep(1)
            print("Sage décision...")

        else:
            print("Choix invalide. Réessayez.")


######################### EVENTS #########################


    def event(self, joueur, case_nombre):

        chance_event = random.randint(1, 100)

        if chance_event <= 30 :
            time.sleep(1)
            print("...")
            time.sleep(2)
            print("Rien ne se passe ici...")
        
        if chance_event > 30 and chance_event <= 70:
            time.sleep(1)
            print("...")
            time.sleep(1)
            print("ARGH! Quelque chose vous attaque!")
            time.sleep(1)

            if case_nombre < 25:
                ennemi = self.generer_ennemi_1()
            if case_nombre >= 25:
                ennemi = self.generer_ennemi_2()      
      
            self.combat(joueur, ennemi)
            chance_drop_loot_combat = random.randint(1, 100)
            if chance_drop_loot_combat < ennemi.niveau:
                print(f"Tiens? Le {ennemi.niveau} {ennemi.nom} gardait un coffre...")
                print("")
                time.sleep(1)
                self.recompense_loot(joueur)


        if chance_event > 70 and chance_event <= 80:
            time.sleep(1)
            print("Vous apercevez de la lumière au fond...")
            time.sleep(1)
            print("C'est une boutique!! Il est temps d'échanger vos objets.")
            self.shop(joueur)


        if chance_event > 80 and chance_event <= 90:
            self.salle_des_coffres(joueur)



        if chance_event > 90 and chance_event <= 95:
            time.sleep(1)
            print("Vous vous trouvez devant la fontaine magique.")
            self.fontaine(joueur)

        
        if chance_event > 95 :
            self.maison_repos(joueur)
            


        
###################### AVENTURE ########################


    def aventure_init(self, joueur):
        case_nombre = 0

        time.sleep(1)
        print("Bienvenue dans ce monde rempli d'aventures! ")
        time.sleep(1)
        print("Vous avancez étape par étape, avec une infinité de surprises et de dangers à chaque pas!")
        time.sleep(1)
        print("Votre objectif est de vaincre le Dragon. Pour cela, vous devrez vous armer de courage et parcourir 50 étapes.")
        print("Ce dernier vous y attend au bout.")
        print("")

        self.aventure(joueur, case_nombre)



                
    def aventure(self, joueur, case_nombre):


        while True:

            time.sleep(1)
            print("")
            print(f"Vous vous trouvez sur la case {case_nombre}/50")
            print("")
            print("╔══════════ ≪ ❈ ≫ ══════════╗")
            print(" Choisissez l'un :")
            print("")
            print(" 1. Avancer")
            print(" 2. Profil")
            print(" 3. Inventaire")
            print(" 4. Quitter")
            print("╚══════════ ≪ ❈ ≫ ══════════╝")
            print("")
            choix_aventure = int(input(""))

            if choix_aventure == 1:

                case_nombre = case_nombre + 1
                print(f"Vous avancez sur la case {case_nombre}.")
                print("")

                if case_nombre == 50:
                    self.event_boss(joueur)
                
                else:
                    self.event(joueur, case_nombre)

            elif choix_aventure == 2:
                joueur.afficher_stats()

            elif choix_aventure == 3:
                self.menu_inventaire(joueur)
            
            elif choix_aventure == 4:

                time.sleep(1)
                print("")
                print("/!\ ATTENTION")
                time.sleep(1)
                print("Si vous retournez au menu, vous perdrez la progression de cette aventure mais vous garderez arme et niveaux.")
                time.sleep(1)
                print("")
                print("╔══════════ ≪ ❈ ≫ ══════════╗")
                print(" Êtes vous sûr?")
                print("")
                print(" 1. Oui")
                print(" 2. Non")
                print("╚══════════ ≪ ❈ ≫ ══════════╝")
                print("")
                choix_quitter_aventure = int(input(""))

                if choix_quitter_aventure == 1:
                    time.sleep(1)
                    case_nombre = 0
                    return self.menu(joueur)

                elif choix_quitter_aventure == 2:
                    time.sleep(1)
                    print("Je le savais. Bon courage!")

                else:
                    print("Choix invalide.")
            
            else:
                time.sleep(1)
                print("Choix invalide.")
                print("")
                time.sleep(1)











    def sauvegarder(self, joueur):
        with open("sauvegarde.pkl", "wb") as fichier:
            pickle.dump(joueur, fichier)

    def charger(self):
        try:
            with open("sauvegarde.pkl", "rb") as fichier:
                joueur = pickle.load(fichier)
            return joueur
        except FileNotFoundError:
            return None

    def run(self):
        joueur_charge = self.charger()
        if joueur_charge:
            print("Partie chargée avec succès!")
            time.sleep(1)
            joueur = joueur_charge
        else:
            joueur = Joueur(input("Choisissez votre nom de héros : "))
        
        self.menu(joueur)

                

if __name__ == "__main__":
    rpg_instance = RPG()
    rpg_instance.run()