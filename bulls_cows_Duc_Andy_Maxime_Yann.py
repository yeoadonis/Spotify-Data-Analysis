#Yeo Duc, Mpengue Maxime, Mbiaya Andy, Yann ekanga
from random import sample
#import vlc
import winsound

def genere_secret() :
    liste = sample(range(10), 4)
    secret = ''.join([str(n) for n in liste])
    return secret

#Exercice 7

def valide_code(code):
    if len(code) != 4:
        return False
    for i in range(4):
        if not code[i].isdigit():
            return False
        for j in range(i+1, 4):
            if code[i] == code[j]:
                return False
    return True

assert valide_code("1234") == True
assert valide_code("1351") == False
assert valide_code("135") == False
assert valide_code("CODE") == False

#Exercice 8
def demande():
    while True:
        code = input("Entrer un code valide : ")
        if valide_code(code):
            return code

#Exemple d'affichage
""">>> demande()
Entrer un code valide : 1111
Entrer un code valide : 84207
Entrer un code valide : ABCD
Entrer un code valide : 5491
"""

#Exercice 9
def tentative(code, secret) :
    bulls = 0
    cows = 0
    for i in range(4) :
        if code[i] == secret[i]:
            bulls += 1
        elif secret[i] in code:
            cows += 1
    return bulls, cows

assert tentative("1234", "1234") == (4, 0)
assert tentative("4123", "1234") == (0, 4)
assert tentative("4231", "1234") == (2, 2)
assert tentative("9t60", "1234") == (0, 0)

#Exercice 10
def affichage (codes , secret):
    for i in range(len(codes)) :
        bulls, cows = tentative(codes[i], secret)
        print(f"{i+1}) {codes[i]} {bulls}B {cows}C")

""" 
    affichage(["1234" ,"4121" ,"1231", "9660"] , "1214") :
    1) "1234" 2B 2C
    2) "4121" 0B 4C
    3) "1231" 2B 2C
    4) "9660" 0B 0C
"""

#Exercice 11
def partie():
    winsound.PlaySound(r"C:\Users\andym\OneDrive\Bureau\Python\NSI_Classe\Python_classe\Introduction aux bases python\Les types conctruit\Les Listes\Début de jeu.mp3", winsound.SND_FILENAME)
    print("."*30)

    #Lance une partie du jeu Bulls and Cows.

    # on génère un secret
    secret = genere_secret()
    code = ""
    codes = []
    #print(secret)
    #  on continue jusqu'à ce que le code soit trouvé
    while True:
        # on demande un code à l'utilisateur
        code = demande()
        codes.append(code)
        affichage(codes, secret)
        bulls, cows = tentative(code, secret)
        if bulls == 4:
            print(f"Bravo, vous avez trouvé en {len(codes)} tentative(s)")
            break
    joueurs={"Andy":2,"Maxime":3,"Yann":4,"Adonis":5,"Gaïtan":20}
    print("_"*30)
    for i in joueurs:
        if joueurs[i]>len(codes):
            print(f"vous: {len(codes)}")
        print(f"{i}:{joueurs[i]}")
    print("Autres: Stupide")
    reponse=("y")
    essai=input("voulez vous réessayer et nous époustoufler ? : y/n\n") in reponse
    if essai==True:
        print("\nBien, commençons une nouvelle partie :")
        partie()
    

partie()