# ImageIQ
REST API for photo share

1. Клонуємо репозиторій https://github.com/Vskesha/ImageIQ
2. Відкриваємо проект в IDE
3. Переходимо на гілку `dev`
4. Налаштовуємо віртуальне оточення а poetry. 
Вводимо команди в терміналі   
    `poetry shell`  
    `poetry install`  
5. Створюємо в корені проєкту файл `.env`, копіюємо поля з файлу `.env.example` і дописуємо свої значення полів.
6. Запускаємо 'Docker desctop' і після цього вводимо в терміналі команду  
`docker-compose up -d`  
(має створитися папка postgres-data і база даних по адресі з файлу `.env`)
7. Вводимо в терміналі команду  
`alembic upgrade head`  
(мають створитися таблиці в базі даних)
8. Створюємо свою нову гілку від `dev`, робимо свої зміни.
9. Для запуску сервера запускаємо файл `main` або командою в терміналі  
`uvicorn main:app --host localhost --port 9024 --reload`
10. lkdjskal;fjlk
11. 