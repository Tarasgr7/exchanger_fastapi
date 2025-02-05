FROM python:3.11

# Встановлюємо робочу директорію
WORKDIR /app 

# Копіюємо файл залежностей
COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Копіюємо весь код додатку
COPY ./exchanger /app/exchanger

# Вказуємо команду запуску
CMD ["uvicorn", "exchanger.main:app", "--host", "0.0.0.0", "--port", "80"]






