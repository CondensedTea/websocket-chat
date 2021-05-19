# homework8
Сервис асинхроного веб-чата на основе websockets с сохранением последних 50 сообщений в pub/sub очереди Redis.
Для наглядности предоставлен CLI-клиент для работы с чатом.

### Запуск CLI-клиента
    Нужно перейти в директорию клиента `client` и установить зависимости через `poetry install`. Теперь клиент можно запустить через `python client_app/main.py [NAME]`  

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format

### Build service:
	make build

### Run service
    make up
