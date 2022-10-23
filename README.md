# Дипломный проект Foodgram
## Описание проекта:
Данный сервис служит для публикации своих рецептов в глобальную сеть. Также у пользователей есть возможность добавлять рецепты в избранное, подписываться на авторов и создавать список покупок.
## Настройка сервера:
Подключение к серверу:

    ssh username@server_address 





Обновите индекс пакетов APT и установленные в системе пакеты:

    sudo apt update
    sudo apt upgrade -y

Скопировать файлы docker-compose.yml и nginx.conf:
    
    scp /D/Dev/foodgram-project-react/infra/nginx.conf
    scp /D/Dev/foodgram-project-react/infra/docker-compose.yml

Установите Docker и Docker-compose:

    sudo apt install docker.io
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

Проверить Docker:

    sudo  docker-compose --version

## Действия после деплоя:

Собрать статику:

    docker-compose exec backend python manage.py collectstatic --no-input

Применить миграции:
    
    docker-compose exec backend python manage.py migrate --noinput

Создать суперпользователя:

    docker-compose exec backend python manage.py createsuperuser

Загрузить ингредиенты в базу:
    
    docker-compose exec backend python manage.py import_ingredients


## Суперпользователь:

Логин: admin
Пароль: admin
Почта: admin@admin.ru

## Ссылки:

[HomePage](http://51.250.25.132/recipes)

[Admin](http://51.250.25.132/admin/)

## Автор
Афанасьев Е.Л - [Evgeninio](https://github.com/Evgeninio)
