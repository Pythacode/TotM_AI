import subprocess
import cv2
import numpy as np
import time

def mesure_temps(fonction):
    def wrapper(*args, **kwargs):
        debut = time.time()
        resultat = fonction(*args, **kwargs)
        fin = time.time()
        print(f"Temps d'exécution de {fonction.__name__} : {fin - debut:.5f} secondes")
        return resultat
    return wrapper

@mesure_temps
def capture_screenshot():
    try:
        # Exécute la commande ADB pour capturer l'écran
        result = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        # Convertir le résultat binaire en image
        image_data = result.stdout
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        hauteur, largeur = image.shape[:2]

        # Calculer les nouvelles dimensions (divisées par 2)
        nouvelle_largeur = largeur // 2
        nouvelle_hauteur = hauteur // 2

        # Redimensionner l'image
        image = cv2.resize(image, (nouvelle_largeur, nouvelle_hauteur))

        return image

    except subprocess.CalledProcessError as e:
        print("Erreur lors de la capture d'écran : ", e.stderr.decode())
        return None
    
def locate_player(image):

    # Convertir l'image en espace HSV
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Définir la plage de couleur pour le jaune (en HSV)
    jaune_min = np.array([20, 100, 100])  # Teinte minimale pour le jaune
    jaune_max = np.array([30, 255, 255])  # Teinte maximale pour le jaune

    # Créer un masque pour les pixels jaunes
    masque = cv2.inRange(image_hsv, jaune_min, jaune_max)

    # Trouver les contours des zones jaunes
    contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dessiner les contours sur l'image originale


    for contour in contours:
        # Calculer la boîte englobante du contour
        x, y, w, h = cv2.boundingRect(contour)
        # Dessiner un rectangle autour du personnage détecté

        if y > 400 and y < 800 and w > 40 and h > 40 :

            return x, y, h, w, image_hsv

            break

def possible_direction(image, pos_x, pos_y) :

    w, h = image.shape[:2]

    cv2.rectangle(image, (pos_x - 10, 0), (pos_x + 10, w), (0, 0, 0), 2)
    cv2.rectangle(image, (0, pos_y - 10), (h, pos_y + 10), (0, 0, 0), 2)

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    jaune_min = np.array([0, 0, 0])  # Teinte minimale pour le jaune
    jaune_max = np.array([5, 5, 5])  # Teinte maximale pour le jaune

    # Créer un masque pour les pixels jaunes
    masque = cv2.inRange(image_hsv, jaune_min, jaune_max)
    masque = cv2.bitwise_not(masque)
    contours, _ = cv2.findContours(masque, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print("--")

    for contour in contours:
        # Calculer la boîte englobante du contour
        x, y, w, h = cv2.boundingRect(contour)
        # Dessiner un rectangle autour du personnage détecté
        if (x > pos_x - 10 and x < pos_x + 10 or y > pos_y - 10 and y < pos_y + 10) and h > 10 and w > 10 : 
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Masque', masque)
    cv2.imshow('Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return image


a = 0
while True :
    a+=1
    screenshot = capture_screenshot()
    if screenshot is not None:
        try :
            x, y, h, w, image_hsv = locate_player(screenshot)
        except :
            continue


        #print(f"Capture d'écran sauvegardée sous 'screenshot{a}.png'.\nPosition du joueur : ({x}, {y}).\nPosition centrale : ({x+(w//2)},{y+(h//2)})")

        screenshot = possible_direction(screenshot, x+(w//2), y+(h//2))

        cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.imwrite(f"screenshot{a}.png", cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV))

        #time.sleep(0.5)
