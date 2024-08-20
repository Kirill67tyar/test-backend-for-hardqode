## test-backend-for-hardqode 

Вы можете развернуть проект двумя способами: 
1.  через venv
2. через Docker Compose


## Инструкция как развернуть в докере

У вас есть возможность развернуть проект в Docker через конфиг для Docker Compose. Вы можете воспользоваться файлом docker-compose.yml и собрать образы локально в директориях проекта.
```
1. Клонируйте репозиторий к себе на компьютер

   git clone git@github.com:Kirill67tyar/test-backend-for-hardqode.git
   
   или

   git clone https://github.com/Kirill67tyar/test-backend-for-hardqode.git

2. Находясь в корневой директории проекта введите команду

touch .env

3. Откройте .env для редактирования

4. Перенесите туда следующие константы, обратите внимание что константа DB_HOST равна db (DB_HOST=db)

POSTGRES_USER= # пользователь который будет подключаться к базе данных
POSTGRES_PASSWORD= # пароль для подключения к базе данных
POSTGRES_DB= # имя базы данных
DB_HOST=db # хост базы данных, должен быть именно db
DB_PORT= # порт базы данных
SECRET_KEY= # секретный ключ можно сгенерировать - https://djecrety.ir/
ALLOWED_HOSTS=127.0.0.1 localhost
TEST_DB=False  # True использовать SQLite, False использовать PostgreSQL

5. Находясь в корневой директории проекта введите команду, чтобы собрать образы локально в директориях проекта:

   sudo docker compose up

6. Проверьте, что все нужные контейнеры запущены (должны быть запущены контейнеры):

   sudo docker compose ps

7. После того как проект развернулся на вашем компьютере, соберите статику django:

   sudo docker compose exec backend python manage.py collectstatic

8. Копируйте статику:

   sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/

9. Примените миграции:

   sudo docker compose exec backend python manage.py migrate

10. Создайте суперпользователя:
   
   sudo docker compose exec backend python manage.py createsuperuser

11. Обратите внимание что контейнер gateway настроен на порт 8080

   http://127.0.0.1:8080/api/v1/courses/
```

## Инструкция как развернуть через виртуальное окружение
```
1. Клонируйте репозиторий к себе на компьютер

   git clone git@github.com:Kirill67tyar/test-backend-for-hardqode.git
   
   или

   git clone https://github.com/Kirill67tyar/test-backend-for-hardqode.git

2. установите виртуальное окружение в корневой директории:

   python3 -m venv venv

3. включите виртуальное окружение:

   source venv/bin/activate

4. установите зависимости:

   python -m pip install --upgrade pip
   pip install -r requirements.txt

5. Перейдите в папку product и выполните миграции:
   
   cd product
   python manage.py migrate

6. Создайте суперпользователя:
   
   python manage.py createsuperuser

7. Запустите проект:
   
   python manage.py runserver

8. Проект доступен на порту 8000

   http://127.0.0.1:8000/api/v1/courses/

```

## Авторство

#### Backend

 1. [HardQode | Веб-студия со стилем](https://hardqode.com/).
 2. [Кирилл Богомолов](https://github.com/Kirill67tyar).
