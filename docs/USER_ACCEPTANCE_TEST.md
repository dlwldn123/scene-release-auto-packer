# Plan Recette Utilisateur - eBook Scene Packer v2

**Date** : 2025-11-03  
**Version** : 1.0.0

---

## 🎯 Objectif

Définir le plan de recette utilisateur pour valider que l'application répond aux besoins utilisateurs et fonctionne correctement en conditions réelles.

---

## 📋 Scénarios Utilisateur

### Scénario 1 : Création Release Complète

**User Story** :
> En tant qu'utilisateur, je veux créer une nouvelle release complète via le wizard 9 étapes pour packager un eBook selon les règles Scene.

**Critères d'Acceptation** :
- [ ] Utilisateur peut naviguer dans le wizard (étapes 1-9)
- [ ] Utilisateur peut sélectionner un groupe Scene
- [ ] Utilisateur peut sélectionner un type de release (EBOOK, DOCS, TV)
- [ ] Utilisateur peut sélectionner une règle applicable
- [ ] Utilisateur peut uploader un fichier (local ou URL distante)
- [ ] Utilisateur peut voir les résultats de l'analyse
- [ ] Utilisateur peut éditer les métadonnées
- [ ] Utilisateur peut sélectionner un template NFO
- [ ] Utilisateur peut configurer les options de packaging
- [ ] Utilisateur peut sélectionner une destination FTP/SSH
- [ ] Release est créée avec succès
- [ ] Job de packaging est créé avec succès

**Étapes Détaillées** :
1. Se connecter à l'application
2. Naviguer vers "Nouvelle Release"
3. **Étape 1** : Saisir nom groupe (ex: "TestGroup")
4. Cliquer "Next"
5. **Étape 2** : Sélectionner type "EBOOK"
6. Cliquer "Next"
7. **Étape 3** : Sélectionner une règle (ex: "[2022] eBOOK")
8. Cliquer "Next"
9. **Étape 4** : Uploader fichier (drag & drop ou URL)
10. Cliquer "Next"
11. **Étape 5** : Vérifier résultats analyse
12. Cliquer "Next"
13. **Étape 6** : Éditer métadonnées si nécessaire
14. Cliquer "Next"
15. **Étape 7** : Sélectionner template NFO
16. Cliquer "Next"
17. **Étape 8** : Configurer options packaging
18. Cliquer "Next"
19. **Étape 9** : Sélectionner destination
20. Cliquer "Finaliser"
21. Vérifier redirection vers liste releases
22. Vérifier release créée avec statut "ready"

**Résultat Attendu** :
- Release créée avec succès
- Job de packaging créé
- Métadonnées correctes
- Conformité Scene respectée

---

### Scénario 2 : Gestion Rules

**User Story** :
> En tant qu'utilisateur, je veux gérer les règles Scene (liste, recherche, upload, téléchargement) pour m'assurer d'avoir les règles à jour.

**Critères d'Acceptation** :
- [ ] Utilisateur peut voir la liste des règles locales
- [ ] Utilisateur peut rechercher une règle
- [ ] Utilisateur peut uploader une règle locale
- [ ] Utilisateur peut télécharger une règle depuis scenerules.org
- [ ] Utilisateur peut éditer une règle
- [ ] Utilisateur peut supprimer une règle

**Étapes Détaillées** :
1. Se connecter à l'application
2. Naviguer vers "Rules"
3. Vérifier liste des règles affichée
4. Utiliser recherche pour filtrer règles
5. Télécharger une règle depuis scenerules.org
6. Vérifier règle ajoutée à la liste
7. Uploader une règle locale
8. Vérifier règle ajoutée
9. Éditer une règle
10. Vérifier modifications sauvegardées
11. Supprimer une règle
12. Vérifier règle supprimée

**Résultat Attendu** :
- Liste rules affichée correctement
- Recherche fonctionne
- Upload/téléchargement fonctionne
- Édition/suppression fonctionne

---

### Scénario 3 : Administration

**User Story** :
> En tant qu'administrateur, je veux gérer les utilisateurs et rôles pour contrôler l'accès à l'application.

**Critères d'Acceptation** :
- [ ] Admin peut voir la liste des utilisateurs
- [ ] Admin peut créer un nouvel utilisateur
- [ ] Admin peut éditer un utilisateur
- [ ] Admin peut attribuer des rôles à un utilisateur
- [ ] Admin peut supprimer un utilisateur
- [ ] Admin peut créer un nouveau rôle
- [ ] Admin peut attribuer des permissions à un rôle

**Étapes Détaillées** :
1. Se connecter en tant qu'admin
2. Naviguer vers "Users"
3. Vérifier liste utilisateurs affichée
4. Créer un nouvel utilisateur
5. Attribuer un rôle à l'utilisateur
6. Vérifier utilisateur créé avec rôle
7. Éditer l'utilisateur
8. Vérifier modifications sauvegardées
9. Naviguer vers "Roles"
10. Créer un nouveau rôle
11. Attribuer des permissions au rôle
12. Vérifier rôle créé avec permissions

**Résultat Attendu** :
- Gestion utilisateurs fonctionne
- Gestion rôles fonctionne
- Permissions appliquées correctement

---

### Scénario 4 : Dashboard et Statistiques

**User Story** :
> En tant qu'utilisateur, je veux voir les statistiques du dashboard pour avoir une vue d'ensemble de mon activité.

**Critères d'Acceptation** :
- [ ] Dashboard affiche statistiques globales
- [ ] Dashboard affiche statistiques utilisateur
- [ ] Statistiques sont à jour
- [ ] Navigation onglets fonctionne

**Étapes Détaillées** :
1. Se connecter à l'application
2. Vérifier dashboard affiché par défaut
3. Vérifier statistiques affichées :
   - Total releases
   - Total jobs
   - Mes releases
   - Mes jobs
4. Naviguer entre onglets
5. Vérifier statistiques mises à jour

**Résultat Attendu** :
- Dashboard affiche statistiques correctes
- Navigation fonctionne
- Statistiques à jour

---

### Scénario 5 : Gestion Releases

**User Story** :
> En tant qu'utilisateur, je veux gérer mes releases (liste, filtres, recherche, édition) pour suivre mes releases.

**Critères d'Acceptation** :
- [ ] Utilisateur peut voir la liste de ses releases
- [ ] Utilisateur peut filtrer par type, status, user_id
- [ ] Utilisateur peut rechercher dans les métadonnées
- [ ] Utilisateur peut trier les releases
- [ ] Utilisateur peut éditer une release
- [ ] Utilisateur peut supprimer une release

**Étapes Détaillées** :
1. Se connecter à l'application
2. Naviguer vers "Releases"
3. Vérifier liste releases affichée
4. Filtrer par type "EBOOK"
5. Vérifier résultats filtrés
6. Rechercher "test" dans métadonnées
7. Vérifier résultats recherche
8. Trier par date de création (desc)
9. Vérifier tri appliqué
10. Éditer une release
11. Modifier métadonnées
12. Sauvegarder modifications
13. Vérifier modifications sauvegardées

**Résultat Attendu** :
- Liste releases affichée correctement
- Filtres/recherche/tri fonctionnent
- Édition fonctionne

---

## ✅ Processus Validation

### Phase 1 : Tests Interne (Développement)

**Durée** : 1 semaine  
**Participants** : Équipe développement

- [ ] Tests tous scénarios
- [ ] Identification bugs
- [ ] Correction bugs critiques
- [ ] Validation fonctionnelle

### Phase 2 : Tests Utilisateurs Bêta

**Durée** : 2 semaines  
**Participants** : Utilisateurs bêta (5-10 utilisateurs)

- [ ] Recrutement utilisateurs bêta
- [ ] Sessions tests utilisabilité
- [ ] Collecte feedback
- [ ] Analyse résultats
- [ ] Plan améliorations

### Phase 3 : Validation Finale

**Durée** : 1 semaine  
**Participants** : Équipe + Utilisateurs bêta

- [ ] Tests scénarios complets
- [ ] Validation corrections
- [ ] Validation performance
- [ ] Validation accessibilité
- [ ] Go/No-Go production

---

## 📊 Critères de Réussite

### Fonctionnels

- ✅ **100% scénarios passent** sans erreurs critiques
- ✅ **Temps réponse** < 200ms (p95)
- ✅ **Taux erreurs** < 0.1%
- ✅ **Accessibilité** WCAG 2.2 AA conforme

### Utilisabilité

- ✅ **Satisfaction utilisateur** ≥ 4/5
- ✅ **Temps apprentissage** < 30 min
- ✅ **Taux complétion** scénarios ≥ 90%

---

## 🔗 Références

- User Stories : `docs/PRDs/`
- Test Plan : `docs/TEST_PLAN.md`
- Design System : `docs/DESIGN_SYSTEM_UI_UX.md`

---

**Dernière mise à jour** : 2025-11-03
