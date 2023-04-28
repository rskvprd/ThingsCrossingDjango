# ThingsCrossingDjango
Простейший backend для мобильного приложения ThingsCrossing, написанный на фреймворке Django + Django Rest Framework.
## Установка на локальное устройство:
1. Склонируйте репозиторий.
2. Создайте виртуальное окружение ```python -m venv .\venv```
3. Активируйте виртуальное окружение с помощью ```.\venv\Scripts\activate```
4. Скачайте библиотеки из ```requirements.txt``` с помощью команды ```pip install -r requirements.txt```
5. Создайте файл окружения ```.env``` в корневой папке проекта и поместите туда секретный ключ django.
Создать данный ключ можно при помощи ```django.core.management.utils.get_random_secret_key()``` после запуска ```django-admin shell```.
Гайд: https://stackoverflow.com/questions/15209978/where-to-store-secret-keys-django
6. Запустите командой ```python manage.py runserver 0.0.0.0:8000```

Теперь вы можете зайти на своё API через браузер устройства, находящегося в одной локальной сети с хостом (в том числе с самого хоста), вбив в поисковую строку ```http://127.0.0.1:8000```
