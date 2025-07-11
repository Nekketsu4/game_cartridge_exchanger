FROM python:3.10-slim

COPY . .
WORKDIR .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "main.py"]