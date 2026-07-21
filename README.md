# Inspire Piazo pour Home Assistant

Intégration personnalisée Home Assistant permettant de piloter un plafonnier
Inspire Piazo en 433,92 MHz à travers une passerelle RFXCOM RFXtrx.

Chaque plafonnier apparaît comme une entité `light` native avec :

- marche et arrêt ;
- réglage de la luminosité ;
- quatre paliers réels à 30, 50, 75 et 100 % ;
- restauration du dernier état estimé après un redémarrage.

## Prérequis

- Home Assistant 2024.12 ou plus récent ;
- une passerelle RFXCOM RFXtrx compatible Lighting4/PT2262 ;
- l’intégration officielle
  [RFXCOM RFXtrx](https://www.home-assistant.io/integrations/rfxtrx/)
  installée et opérationnelle.

## Installation avec HACS

1. Dans HACS, ouvrir **Intégrations**.
2. Ouvrir le menu en haut à droite, puis **Dépôts personnalisés**.
3. Ajouter `https://github.com/tof43/inspire-piazo-home-assistant` avec la
   catégorie **Intégration**.
4. Rechercher **Inspire Piazo**, puis télécharger l’intégration.
5. Redémarrer Home Assistant.

## Installation manuelle

Copier le dossier
`custom_components/inspire_piazo` dans le dossier `custom_components` de la
configuration Home Assistant, puis redémarrer Home Assistant. Le fichier final
doit notamment se trouver à cet emplacement :

```text
<config>/custom_components/inspire_piazo/manifest.json
```

## Configuration

1. Ouvrir **Paramètres > Appareils et services**.
2. Choisir **Ajouter une intégration**.
3. Rechercher **Inspire Piazo**.
4. Saisir le nom du plafonnier et son code de télécommande.

Le code connu pour le plafonnier étudié est `F120`. Il correspond aux quatre
premiers chiffres du mot radio de 24 bits : par exemple `F120` dans la commande
ON `F12001`.

Pour ajouter plusieurs plafonniers, répéter simplement cette configuration avec
un nom et un code de télécommande différents. Deux plafonniers utilisant le même
code radio ne peuvent pas être commandés indépendamment ; il s’agit d’une limite
du protocole radio, pas de Home Assistant.

## Comportement de la luminosité

Le plafonnier ne fournit que quatre valeurs absolues. Home Assistant arrondit
donc le curseur au palier disponible le plus proche :

| Valeur demandée | Commande envoyée |
| ---: | ---: |
| 1 à 40 % | 30 % |
| 41 à 62 % | 50 % |
| 63 à 87 % | 75 % |
| 88 à 100 % | 100 % |

## Limites connues

- Le protocole est unidirectionnel. Home Assistant affiche le dernier ordre
  envoyé et marque donc l’état comme estimé.
- L’utilisation de la télécommande physique peut désynchroniser l’état affiché.
- Les touches relatives de température de couleur `K+` et `K−` ne sont pas
  exposées : leur amplitude et les bornes Kelvin réelles ne sont pas encore
  mesurées.
- Cette intégration transmet les commandes au service `rfxtrx.send`; elle ne
  remplace pas la configuration de la passerelle RFXtrx.

## Protocole

Les commandes sont envoyées sous forme de paquets Lighting4/PT2262 avec une
impulsion de 390 µs. Pour le code `F120`, les principaux paquets sont :

| Action | Paquet RFXtrx |
| --- | --- |
| ON | `09130000F12001018600` |
| OFF | `09130000F12003018600` |
| 30 % | `09130000F1200F018600` |
| 50 % | `09130000F1200E018600` |
| 75 % | `09130000F12010018600` |
| 100 % | `09130000F12012018600` |

## Désinstallation

Supprimer chaque entrée **Inspire Piazo** dans **Paramètres > Appareils et
services**, désinstaller le dépôt depuis HACS (ou supprimer manuellement le
dossier `custom_components/inspire_piazo`), puis redémarrer Home Assistant.

## Licence

[MIT](LICENSE)
