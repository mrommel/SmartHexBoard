# Smart Hex Board

![pytest workflow](https://github.com/mrommel/SmartHexBoard/workflows/pytesting/badge.svg)
![coverage workflow](https://raw.githubusercontent.com/mrommel/SmartHexBoard/coverage-badge/coverage.svg?raw=true)

Smart test for rendering of hex board 
Javascript based tile visualization (python + django as server)

## Technique

based on 
* Django

## Start

### Start 

### Start redis Service

```
brew services start redis   
```

### Start Web Server

```
# source venv/bin/activate
# python3 manage.py runserver 8081
make run
```

### Start QCluster

```
# source venv/bin/activate
# python3 manage.py qcluster
make run-qcluster
```

## Migrations

```
source venv/bin/activate
python3 manage.py makemigrations
python3 manage.py sqlmigrate smarthexboard 000? <= change this
python3 manage.py migrate
```
or
```
make makemigrations
```

## Translations

### installation

```
brew install gettext
brew link gettext --force
```

### do the translations

```
python3 ../manage.py makemessages -l de -e html,txt,py -e xml
```
translate with poedit

```
python3 ../manage.py compilemessages
```

## Links

* https://realpython.com/django-setup/
* https://www.freepik.com/free-photo/grunge-black-concrete-textured-background_17118014.htm
* https://favicon.io/
* https://www.longitude.one/maps
* https://www.garmuri.com/game_ui/109237
* https://www.behance.net/gallery/125706279/Game-UI-Concept
* https://www.behance.net/gallery/42418323/UI-ART-for-an-UNANNOUNCED-video-game
* https://github.com/Toby-Willsmer/Javascript-flexbox-modal
* https://demos.creative-tim.com/soft-ui-design-system-pro/presentation.html
* https://www.behance.net/gallery/57207157/League-of-Legends-In-Game-UI-Style-Guide-2016
* https://github.com/josephg/noisejs
* https://fontmeme.com/dawngate-font/
* https://transfonter.org/
* https://www.valentinog.com/blog/django-q/
* https://mitchel.me/slippers/docs/template-tags-filters/