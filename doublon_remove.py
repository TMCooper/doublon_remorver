import os
import imagehash
from PIL import Image
from moviepy.editor import VideoFileClip

def get_file_hash(file_path):
    """Calcule le hash du fichier (image ou vidéo)."""
    if file_path.lower().endswith((".jpg", ".png")):
        with Image.open(file_path) as image:
            return str(imagehash.average_hash(image))
    elif file_path.lower().endswith(".mp4"):
        with VideoFileClip(file_path) as video:
            # Sélectionner une image à 30% de la durée totale pour le hash (pour accélérer le processus)
            frame = video.get_frame(video.duration * 0.3)
            image = Image.fromarray((frame * 255).astype('uint8'))
            return str(imagehash.average_hash(image))
    else:
        return None

def count_duplicates(directory):
    """Compte le nombre de doublons d'images et de vidéos dans le répertoire spécifié (y compris les sous-dossiers)."""
    image_hashes = {}
    video_hashes = {}
    duplicates_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            if file_hash:
                if file_path.lower().endswith((".jpg", ".png")):
                    if file_hash in image_hashes:
                        duplicates_count += 1
                    else:
                        image_hashes[file_hash] = file_path
                elif file_path.lower().endswith(".mp4"):
                    if file_hash in video_hashes:
                        duplicates_count += 1
                    else:
                        video_hashes[file_hash] = file_path
    return duplicates_count

def remove_duplicates_and_empty_directories(directory):
    """Supprime les doublons d'images et de vidéos, et les dossiers vides dans le répertoire spécifié (y compris les sous-dossiers)."""
    image_hashes = {}
    video_hashes = {}
    duplicates_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            if file_hash:
                if file_path.lower().endswith((".jpg", ".png")):
                    if file_hash in image_hashes:
                        # Image en double détectée
                        duplicates_count += 1
                        existing_image_path = image_hashes[file_hash]
                        existing_image_stat = os.stat(existing_image_path)
                        current_image_stat = os.stat(file_path)
                        if current_image_stat.st_ctime > existing_image_stat.st_ctime:
                            print(f"Suppression du doublon d'image : {file_path}")
                            os.remove(file_path)
                        else:
                            print(f"Suppression du doublon d'image : {existing_image_path}")
                            os.remove(existing_image_path)
                            image_hashes[file_hash] = file_path
                    else:
                        # Conserver l'image originale
                        image_hashes[file_hash] = file_path
                elif file_path.lower().endswith(".mp4"):
                    if file_hash in video_hashes:
                        # Vidéo en double détectée
                        duplicates_count += 1
                        existing_video_path = video_hashes[file_hash]
                        existing_video_stat = os.stat(existing_video_path)
                        current_video_stat = os.stat(file_path)
                        if current_video_stat.st_ctime > existing_video_stat.st_ctime:
                            print(f"Suppression du doublon de vidéo : {file_path}")
                            os.remove(file_path)
                        else:
                            print(f"Suppression du doublon de vidéo : {existing_video_path}")
                            os.remove(existing_video_path)
                            video_hashes[file_hash] = file_path
                    else:
                        # Conserver la vidéo originale
                        video_hashes[file_hash] = file_path

    # Supprimer les dossiers vides dans le répertoire spécifié et ses sous-dossiers
    for root, dirs, _ in os.walk(directory, topdown=True):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                # Le dossier est vide, le supprimer
                print(f"Suppression du dossier vide : {folder_path}")
                os.rmdir(folder_path)

    return duplicates_count

def get_original_filename(file_paths):
    """Retourne le nom du fichier original en fonction de la date de création la plus ancienne."""
    return min(file_paths, key=lambda path: os.stat(path).st_ctime)

def find_duplicates(directory):
    """Trouve les doublons d'images et de vidéos dans le répertoire spécifié (y compris les sous-dossiers)."""
    image_duplicates = {}
    video_duplicates = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            if file_hash:
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                if file_path.lower().endswith((".jpg", ".png")):
                    if file_hash in image_duplicates:
                        image_duplicates[file_hash].append(file_path)
                    else:
                        image_duplicates[file_hash] = [file_path]
                elif file_path.lower().endswith(".mp4"):
                    if file_hash in video_duplicates:
                        video_duplicates[file_hash].append(file_path)
                    else:
                        video_duplicates[file_hash] = [file_path]

    return image_duplicates, video_duplicates

def display_image_duplicates(image_duplicates):
    """Affiche les doublons d'images avec l'original en premier et ses doublons en dessous."""
    for original_hash, duplicate_list in image_duplicates.items():
        original_file = get_original_filename(duplicate_list)
        duplicate_list = [f for f in duplicate_list if f != original_file]
        print(f"[ORIGINAL] {original_file}")
        for idx, duplicate in enumerate(duplicate_list, start=1):
            print(f"  [Doublon {idx}] : {duplicate}")
        print()

def display_video_duplicates(video_duplicates):
    """Affiche les doublons de vidéos avec l'original en premier et ses doublons en dessous."""
    for original_hash, duplicate_list in video_duplicates.items():
        original_file = get_original_filename(duplicate_list)
        duplicate_list = [f for f in duplicate_list if f != original_file]
        print(f"[ORIGINAL] {original_file}")
        for idx, duplicate in enumerate(duplicate_list, start=1):
            print(f"  [Doublon {idx}] : {duplicate}")
        print()

def main():
    target_directory = "."  # Mettez ici le chemin du répertoire cible

    while True:
        image_duplicates, video_duplicates = find_duplicates(target_directory)
        duplicates_count = count_duplicates(target_directory)
        print(f"Nombre de doublons trouvés : {duplicates_count}")

        if duplicates_count == 0:
            print("Aucun doublon trouvé.")
            break

        if duplicates_count > 0:
            option = input("Que voulez-vous faire ?\n1. Afficher les doublons d'images\n2. Afficher les doublons de vidéos\n3. Supprimer les doublons d'images et de vidéos\n4. Localiser les doublons d'images et de vidéos\n5. Quitter\n")

            if option == "1":
                if image_duplicates:
                    has_duplicates = False
                    for original_hash, duplicate_list in image_duplicates.items():
                        if len(duplicate_list) > 1:
                            has_duplicates = True
                            original_file = get_original_filename(duplicate_list)
                            duplicate_list = [f for f in duplicate_list if f != original_file]
                            print(f"[ORIGINAL] {original_file}")
                            for idx, duplicate in enumerate(duplicate_list, start=1):
                                print(f"  [Doublon {idx}] : {duplicate}")
                            print()
                    if not has_duplicates:
                        print("Aucun doublon d'images trouvé.")
                else:
                    print("Aucun doublon d'images trouvé.")
            elif option == "2":
                if video_duplicates:
                    has_duplicates = False
                    for original_hash, duplicate_list in video_duplicates.items():
                        if len(duplicate_list) > 1:
                            has_duplicates = True
                            original_file = get_original_filename(duplicate_list)
                            duplicate_list = [f for f in duplicate_list if f != original_file]
                            print(f"[ORIGINAL] {original_file}")
                            for idx, duplicate in enumerate(duplicate_list, start=1):
                                print(f"  [Doublon {idx}] : {duplicate}")
                            print()
                    if not has_duplicates:
                        print("Aucun doublon de vidéos trouvé.")
                else:
                    print("Aucun doublon de vidéos trouvé.")
            elif option == "3":
                print(f"Nombre total de doublons à supprimer : {duplicates_count}")
                confirmation = input("Attention ! Cette opération supprimera tous les doublons d'images et de vidéos dans le répertoire cible. Êtes-vous sûr de vouloir continuer ? (Oui/Non) ")
                if confirmation.lower() == "oui":
                    remove_duplicates_and_empty_directories(target_directory)
                    print(f"{duplicates_count} doublons ont été supprimés.")
                else:
                    print("Suppression annulée.")
                    break
            elif option == "4":
                if image_duplicates or video_duplicates:
                    has_duplicates = False
                    if image_duplicates:
                        for original_hash, duplicate_list in image_duplicates.items():
                            if len(duplicate_list) > 1:
                                has_duplicates = True
                                original_file = get_original_filename(duplicate_list)
                                duplicate_list = [f for f in duplicate_list if f != original_file]
                                print(f"[ORIGINAL] {original_file}")
                                for idx, duplicate in enumerate(duplicate_list, start=1):
                                    print(f"  [Doublon {idx}] : {duplicate}")
                                print()
                    if video_duplicates:
                        for original_hash, duplicate_list in video_duplicates.items():
                            if len(duplicate_list) > 1:
                                has_duplicates = True
                                original_file = get_original_filename(duplicate_list)
                                duplicate_list = [f for f in duplicate_list if f != original_file]
                                print(f"[ORIGINAL] {original_file}")
                                for idx, duplicate in enumerate(duplicate_list, start=1):
                                    print(f"  [Doublon {idx}] : {duplicate}")
                                print()
                    if not has_duplicates:
                        print("Aucun doublon trouvé.")
                else:
                    print("Aucun doublon trouvé.")
            elif option == "5":
                print("Programme terminé.")
                break
            else:
                print("Option invalide.")
        else:
            print("Aucun doublon trouvé.")

if __name__ == "__main__":
    main()