<div align="center">
	<h1>🔍 Card Scanner FR (Flask)</h1>
	<p>Scanner perceptuel d'images pour identifier des cartes TCG sur le marché francophone.</p>
	<p>
		<strong>Rapide · Open Source · Respectueux de la vie privée</strong>
	</p>
	<p>
		<a href="https://scanmacarte.fr" target="_blank" rel="noopener">🌐 Site</a> ·
		<a href="https://github.com/nazimboudeffa/card-scanner-fr-flask" target="_blank" rel="noopener">Code source</a> ·
		<a href="https://www.tipeee.com/nazimboudeffa" target="_blank" rel="noopener">💝 Faire un don</a>
	</p>
</div>

---

## 📌 Objectif

Identifier rapidement une carte TCG à partir d'une photo (webcam ou upload) en comparant son **hash perceptuel** avec une base locale de références francophones.

Le projet met l'accent sur :
1. 🎯 Focus sur le marché francophone (noms, extensions FR)  
2. 🔐 Aucune donnée envoyée à des services tiers  
3. 🛠️ Simplicité de déploiement (Flask + SQLite)  
4. 🚀 Performance et extensibilité (ajout futur d'autres TCG et algorithmes)  

---

## ✨ Fonctionnalités Actuelles

- Capture image via caméra (mobile ou desktop)
- Upload d'une image locale
- Calcul de hash perceptuel : `pHash`, `dHash`, `aHash`, `wHash`
- Recherche des correspondances les plus proches (distance de Hamming)
- Base SQLite existante avec deux tables : `hashs` et `cards`
- Interface web moderne (HTML/CSS/JS vanilla)

### 🧱 Schéma de la base

| Table | Colonnes |
|-------|----------|
| `hashs` | `file_name`, `hash` |
| `cards` | `number`, `set_name`, `rarity`, `card_name`, `file_name` |

Correspondance via `file_name`.

---

## 🚀 Installation

### Prérequis
- Python 3.10+
- pip

### Cloner le dépôt
```bash
git clone https://github.com/nazimboudeffa/card-scanner-fr-flask.git
cd card-scanner-fr-flask
```

### Installer les dépendances
```bash
pip install -r requirements.txt
```

### Lancer l'application
```bash
python app.py
# Puis ouvrir http://localhost:5000
```

> La base `database.db` doit déjà exister avec ses tables. Le code ne crée plus de schéma automatiquement.

---

## 🖥️ Utilisation
1. Accéder à l'interface web.
2. Choisir le type et la taille du hash (par défaut pHash / 16).
3. Capturer via la caméra ou charger une image.
4. Voir le hash calculé et la carte la plus proche / matches.
5. Ajuster la distance maximum selon la qualité de l'image.

---

## 🛣️ Roadmap

- [ ] Ajout d'autres extensions Pokémon FR
- [ ] Support d'autres TCG (Yu-Gi-Oh!, Magic, Lorcana...)
- [ ] Interface d'administration pour enrichir la base
- [ ] Export / import de hash batch
- [ ] Tests automatisés (PyTest)
- [ ] Cache mémoire des hashs pour performance
- [ ] API REST publique (format JSON standardisé)
- [ ] Amélioration UI accessibilité (a11y)

Si une de ces tâches vous intéresse, ouvrez une issue ou une PR !

---

## 🤝 Contribuer

Toutes les contributions sont bienvenues : corrections, docs, nouvelles features, optimisation d'algorithmes.

### Démarrer une contribution
1. Forker le dépôt
2. Créer une branche descriptive : `feature/ajout-dhash` ou `fix/erreur-hamming`
3. Faire des commits clairs (en français ou anglais, mais concis)
4. Tester manuellement avant PR
5. Ouvrir une Pull Request avec :
	 - Contexte du changement
	 - Avant / Après (si UI)
	 - Impact sur la base / performances

### Conseils Qualité
- Éviter d'ajouter des frameworks lourds
- Respecter le style simple actuel (Flask + vanilla JS)
- Préserver la compatibilité mobile
- Documenter les algorithmes si modifiés

### Idées faciles pour commencer
- Ajouter un script d'import massifs de hash
- Ajouter un mode "read-only" via `?mode=ro`
- Ajouter un endpoint `/health` pour monitoring
- Améliorer la section donation dans l'UI

---

## 💝 Soutenir le projet

Ce projet est maintenu sur du temps libre. Votre soutien permet :
- Hébergement et nom de domaine
- Acquisition / scan de nouvelles cartes
- Amélioration de la précision des algorithmes
- Développement des prochaines fonctionnalités

👉 Faire un don récurrent ou ponctuel : **https://www.tipeee.com/nazimboudeffa**

Même 1€ aide réellement. Vous pouvez aussi :
- Mettre une ⭐ sur GitHub
- Partager le projet
- Proposer une extension à intégrer

Merci pour votre soutien 🙏

---

## 🧪 Tests (à venir)
Des scénarios PyTest simples seront ajoutés :
- Calcul de hash stable
- Recherche exacte / proche
- Gestion des images invalides

---

## 📄 Licence

Sous licence MIT – libre utilisation, modification, redistribution.

---

## 📬 Contact
- Auteur : @nazimboudeffa
- Issues : via GitHub
- Contributions : Pull Requests bien structurées

---

Made with ❤️ pour la communauté francophone TCG.