[![Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)]("http://creativecommons.org/licenses/by-nc-sa/4.0/" "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License")  
This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

---

# Projet NAS Groupe 10

---

## Description

Projet NAS Groupe 10 est une solution d'automatisation pour les services BGP VPN dans un réseau. Ce projet est basé sur GNS3, un outil de simulation de réseau graphique, et permet de simplifier la création et la configuration des routeurs pour les réseaux VPN. Le projet se compose de deux programmes principaux : JsonGenerator.py et main.py.

Le programme JsonGenerator.py est responsable de la conversion de la topologie du réseau créée dans GNS3 en un fichier JSON. Pour cela, il utilise les rectangles colorés pour représenter les différents liens VPN entre les routeurs, chaque couleur représentant un lien VPN distinct (un même client).

Le programme main.py, quant à lui, utilise le fichier JSON généré précédemment pour créer automatiquement les configurations des routeurs pour les services BGP VPN.

## Utilisation

1. Lancez GNS3 et créez votre topologie réseau.
2. Utilisez des rectangles colorés pour représenter les liens VPN entre les routeurs, en respectant la règle suivante : une couleur unique pour chaque lien VPN (un même client).
3. Enregistrez et fermez votre topologie GNS3.
4. Lancez le programme JsonGenerator.py pour convertir la topologie en un fichier network.json.
5. Exécutez le programme main.py pour générer automatiquement les configurations des routeurs à partir du fichier network.json.

À la fin de ces étapes, vous aurez créé et configuré automatiquement les routeurs pour les services BGP VPN, simplifiant ainsi le processus de mise en place et de gestion de votre réseau.


## Auteurs

* **Valentin LEMAIRE** - *Initial work* - [Valentin Lemaire](https://github.com/28Pollux28)
* **Gaspard O'MAHONY** - *Initial work* - [gaspardomahony](https://github.com/gaspardomahony)
* **Baptiste Parpette** - *Initial work* - [Baptiste Parpette](https://github.com/baptisteparpette)
* **Valentin RENAUD** - *Initial work* - [Valentin Renaud](https://github.com/Valdyzer)
* **Samar CHAMKI** - *Initial work* - [Samar CHAMKI](https://github.com/)
* **Noa TEDGHI** - *Initial work* - [Noa TEDGHI](https://github.com/ntedghi)

---

## License

This project is licensed under the terms of the CC BY-NC-SA 4.0 license.

