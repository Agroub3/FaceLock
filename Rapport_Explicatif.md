# Rapport Explicatif : Projet FaceLock

## 1. Introduction
Le projet **FaceLock** est une application d'authentification faciale conçue pour sécuriser l'accès à une session Windows. Conformément au cahier des charges, l'objectif principal est de développer un système capable de verrouiller automatiquement la session lorsque l'utilisateur s'absente, et de la maintenir active (ou de la déverrouiller) lorsqu'il est reconnu devant la webcam.

Ce projet met en œuvre un pipeline complet de vision par ordinateur, intégrant la détection, l'alignement et la reconnaissance faciale via des modèles de Deep Learning, tout en respectant scrupuleusement les principes de protection de la vie privée (Privacy by Design).

## 2. Architecture Technique et Choix Technologiques

L'architecture du projet a été divisée en plusieurs modules distincts pour garantir une séparation claire des responsabilités, facilitant ainsi la maintenance et l'évolutivité du code.

### 2.1. Module d'Acquisition (`camera_handler.py`)
Ce module utilise la bibliothèque **OpenCV** (`cv2`) pour capturer le flux vidéo de la webcam en temps réel. Il gère l'ouverture, la lecture des frames et la fermeture propre du périphérique vidéo.

### 2.2. Module de Détection (`face_detector.py`)
Pour la détection faciale, nous avons opté pour **MediaPipe** de Google. Ce choix est justifié par sa rapidité d'exécution (optimisé pour CPU) et sa facilité d'installation sur Windows, contrairement à d'autres solutions comme `dlib` qui nécessitent souvent des compilations complexes avec CMake. MediaPipe fournit les coordonnées précises (boîtes englobantes) des visages présents dans l'image.

### 2.3. Module d'Extraction de Caractéristiques (`face_encoder.py`)
C'est le cœur du système de Deep Learning. Nous avons utilisé le modèle **FaceNet** (via la bibliothèque `keras-facenet`). Ce modèle transforme l'image recadrée d'un visage en un vecteur numérique dense de 512 dimensions, appelé *embedding*. Ce vecteur représente les caractéristiques uniques du visage.

### 2.4. Module d'Authentification (`face_authenticator.py`)
Ce module compare l'embedding du visage capturé en temps réel avec ceux stockés dans la base de données. La comparaison s'effectue en calculant la **distance cosinus** entre les deux vecteurs (via `scipy.spatial.distance.cosine`). Si cette distance est inférieure à un seuil prédéfini (threshold de 0.4), le système considère qu'il s'agit de la même personne.

### 2.5. Module de Base de Données (`database.py`)
Nous avons utilisé **SQLite**, une base de données légère et intégrée à Python, pour stocker les informations des utilisateurs. Les embeddings (vecteurs numpy) sont convertis au format JSON pour être stockés sous forme de texte dans la base de données.

### 2.6. Module de Contrôle Système (`system_controller.py`)
Ce module interagit avec l'API système de Windows via la bibliothèque `ctypes`. Il utilise la fonction `LockWorkStation` de `user32.dll` pour verrouiller la session lorsque l'utilisateur n'est plus détecté devant l'écran pendant un certain temps (timeout de 10 secondes).

### 2.7. Interface Utilisateur (`main.py`)
L'interface graphique a été développée avec **CustomTkinter**, offrant un design moderne et sombre. Elle permet à l'utilisateur de s'enrôler (ajouter son visage à la base de données) et de démarrer ou d'arrêter la surveillance vidéo.

## 3. Analyse des Risques et Conformité (Privacy by Design)

L'une des innovations majeures de ce projet est l'intégration des principes de protection de la vie privée dès la conception, en écho aux exigences du RGPD et des normes ISO (comme l'ISO 27701).

### 3.1. Minimisation des Données
Le système applique strictement le principe de minimisation des données. Lors de l'enrôlement d'un utilisateur, la photo originale capturée par la webcam n'est **jamais stockée** sur le disque dur. Seul le vecteur mathématique (l'embedding) généré par le modèle FaceNet est conservé dans la base de données.

### 3.2. Irréversibilité Biométrique
L'embedding stocké est une représentation unidirectionnelle des caractéristiques faciales. Il est mathématiquement impossible de reconstruire l'image originale du visage à partir de ce vecteur de 512 dimensions. Ainsi, même en cas de compromission de la base de données, les visages des utilisateurs ne peuvent pas être récupérés.

### 3.3. Traitement Local et Souveraineté
L'intégralité du pipeline de traitement (capture, détection, encodage et comparaison) est exécutée **localement** sur la machine de l'utilisateur. Aucune donnée biométrique ne transite par un réseau ou n'est envoyée vers un serveur cloud externe, garantissant ainsi la souveraineté totale des données.

### 3.4. Droit à l'Oubli
Le module de base de données intègre une fonction `delete_user` permettant de supprimer facilement et définitivement toutes les données associées à un utilisateur, répondant ainsi à l'exigence du droit à l'oubli stipulée par le RGPD.

## 4. Conclusion
Le projet FaceLock démontre avec succès la mise en œuvre d'un système de reconnaissance faciale fonctionnel et sécurisé. En combinant des technologies modernes de Deep Learning (MediaPipe, FaceNet) avec une architecture logicielle robuste et une approche "Privacy by Design", ce projet répond parfaitement aux objectifs pédagogiques et techniques fixés par le cahier des charges.
