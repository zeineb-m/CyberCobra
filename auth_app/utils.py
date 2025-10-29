# # auth_app/utils.py
# import face_recognition
# import os

# def compare_face(stored_encoding, image_path):
#     """
#     Compare un encodage facial stocké avec une nouvelle image.
    
#     Args:
#         stored_encoding (list or numpy.ndarray): Encodage facial de l'utilisateur enregistré.
#         image_path (str): Chemin vers l'image temporaire à comparer.
        
#     Returns:
#         bool: True si le visage correspond, False sinon.
#     """
#     if not os.path.exists(image_path):
#         return False

#     try:
#         # Chargement de l'image
#         unknown_image = face_recognition.load_image_file(image_path)
#         # Extraction des encodages faciaux
#         unknown_encodings = face_recognition.face_encodings(unknown_image)
        
#         if len(unknown_encodings) == 0:
#             # Aucun visage détecté
#             return False
        
#         # Comparaison avec l'encodage stocké
#         match = face_recognition.compare_faces([stored_encoding], unknown_encodings[0])
#         return match[0]

#     except Exception as e:
#         print(f"[compare_face] Erreur lors de la comparaison : {e}")
#         return False
