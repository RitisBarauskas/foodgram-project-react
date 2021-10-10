![example workflow](https://github.com/RitisBarauskas/foodgram-project-react/actions/workflows/main.yaml/badge.svg)

# Foodgram
## продуктовый помощник

С помощью Foodgram можно не просто подобрать подходящий рецепт на завтрак, обед или ужин. С помощью Foodgram можно рассчитать необходимое количество ингердиентов на любое количество персон, добавить все к себе в корзину и рапечатать.
А еще на Foodgram можно добавлять рецепты в избранное, подписываться на любимых авторов-кулинаров и не только.

### Адрес проекта
www.foodgram.website <br>
[62.84.115.42]() - альтернативный адрес

### Компоненты
- backend - образ бэкенда (DRF)
- fronted - образ фронтенда (React)
- postgres - образ базы данных (PostgreSQL)
- nginx - образ веб-сервера

### Установка
1. Клонируйте себе репозиторий:
git clone https://github.com/RitisBarauskas/foodgram-project-react.git
2. Заполните файл .env по образцу. Файл и образец должны находиться в директории backend/foodgram_project/
3. Установите Docker (если он у вас установлен, то можете пропустить этот шаг)
4. Перейдите в папку infra/ <br>
`cd infra`
5. Запустите сборку и docker-compose <br>
`docker-compose up -d --build`

### Первоначальная настройка
1. Запустите миграции<br>
`sudo docker-compose exec infra_backend_1 python manage.py migrate --noinput`
2. Соберите статику<br>
`sudo docker-compose exec infra_backend_1 python manage.py collectstatic --no-input`
3. Создайте суперпользователя<br>
`sudo docker-compose exec infra_backend_1 python manage.py createsuperuser`
4. Загрузите данные ингердиентов (их больше 2000)<br>
`sudo docker-compose exec infra_backend_1  python manage.py loaddata ingredients.json`

### Данные для тестирования на облаке
**email**: admin@foodgram.website <br>
**password**: Pass9876

### Технологии
- Python
- Django Rest Framework
- Docker
- Nginx
- Postgres
- React

### Автор
_Ритис Бараускас, Fullstack-developer_<br>
WA, TG, Mob: +79526578502
