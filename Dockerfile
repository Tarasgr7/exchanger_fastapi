FROM python:3.11

# Встановлюємо робочу директорію
WORKDIR /app 

# Копіюємо файл залежностей
COPY ./requirements.txt /app/requirements.txt

# Встановлюємо залежності
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Копіюємо весь код додатку
COPY ./exchanger /app/exchanger

# Вказуємо команду запуску
CMD ["uvicorn", "exchanger.main:app", "--host", "0.0.0.0", "--port", "80"]






