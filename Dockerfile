# Menggunakan image Python
FROM python:3.11-slim

# Menetapkan working directory
WORKDIR /app

# Install dependensi
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Salin kode aplikasi
COPY . /app/

# Jalankan aplikasi menggunakan Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
