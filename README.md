# CyberCobra

## API Gestion d'équipement

**Note**: L'API utilise maintenant des vues manuelles (APIView) au lieu de ModelViewSet pour un contrôle total.

Endpoints disponibles (protégés par JWT Bearer):

- GET /api/equipements/ — Lister les équipements
- POST /api/equipements/ — Créer un équipement
- GET /api/equipements/{id}/ — Détail d'un équipement
- PUT /api/equipements/{id}/ — Mettre à jour (full update)
- PATCH /api/equipements/{id}/ — Mettre à jour partiellement
- DELETE /api/equipements/{id}/ — Supprimer
- POST /api/equipements/recognize/ — Reconnaître un équipement depuis une image

Schéma Equipement:

- id_equipement: Integer (PK, auto)
- nom: String
- statut: Enum [AUTORISE | INTERDIT | SOUMIS]
- date_ajout: DateTime (auto)
- description: Text (optionnel)

Démarrer le serveur:

1. Crée les migrations et applique-les (déjà fait):
	- python manage.py makemigrations gestion_dequipement
	- python manage.py migrate
2. Lance le serveur:
	- python manage.py runserver

Authentification: utilise /api/auth/login/ pour obtenir les tokens `access` et `refresh`.