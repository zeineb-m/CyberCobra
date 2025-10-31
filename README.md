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

## API Gestion de Caméras

**Note**: L'API utilise des vues manuelles (APIView) avec le même pattern que la gestion d'équipements.

Endpoints disponibles (protégés par JWT Bearer):

- GET /api/cameras/ — Lister les caméras
- POST /api/cameras/ — Créer une caméra
- GET /api/cameras/{id}/ — Détail d'une caméra
- PUT /api/cameras/{id}/ — Mettre à jour (full update)
- PATCH /api/cameras/{id}/ — Mettre à jour partiellement
- DELETE /api/cameras/{id}/ — Supprimer

Schéma Camera:

- id_camera: Integer (PK, auto)
- name: String
- zone: String
- ip_address: IPAddress
- resolution: String (ex: "1080p", "4K")
- status: Enum [RECORDING | OFFLINE | MAINTENANCE]
- date_ajout: DateTime (auto)

## Démarrage du serveur

1. Crée les migrations et applique-les:
	```bash
	python manage.py makemigrations
	python manage.py migrate
	```

2. Lance le serveur:
	```bash
	python manage.py runserver
	```

3. Test des endpoints:
	```bash
	# Test équipements
	python test_crud_endpoints.py
	
	# Test caméras
	python test_camera_endpoints.py
	```

## Authentification

Utilise `/api/auth/login/` pour obtenir les tokens `access` et `refresh`.

## Architecture

- **auth_app**: Gestion des utilisateurs et authentification JWT
- **gestion_dequipement**: CRUD manuel pour les équipements avec reconnaissance d'image
- **gestion_camera**: CRUD manuel pour les caméras de surveillance