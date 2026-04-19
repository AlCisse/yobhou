FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libglx-mesa0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyMuPDF first (has ARM64 wheels in newer versions)
# Then install requirements without triggering PyMuPDF rebuild
RUN pip install --no-cache-dir PyMuPDF==1.24.0 && \
    pip install --no-cache-dir Django==5.0.6 djangorestframework==3.15.1 djangorestframework-simplejwt==5.3.1 gunicorn==21.2.0 && \
    pip install --no-cache-dir paddlepaddle==2.6.2 opencv-python==4.6.0.66 numpy==1.24.3 Pillow==10.0.1 && \
    pip install --no-cache-dir psycopg2-binary==2.9.9 redis==5.0.1 elasticsearch==8.11.0 elasticsearch-dsl==8.11.0 && \
    pip install --no-cache-dir cryptography==41.0.7 python-dotenv==1.0.0 && \
    pip install --no-cache-dir pytest==8.2.0 pytest-django==4.8.0 factory-boy==3.2.1 black==24.4.0 pylint==3.1.0 shapely==2.0.1 pyclipper==1.3.0.post4 scikit-image==0.21.0 && \
    pip install --no-cache-dir paddleocr==2.7.0 --no-deps

# Copy application code
COPY . .

# Create media directory for uploaded files
RUN mkdir -p /app/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Expose port
EXPOSE 8000

# Run Gunicorn for production (not runserver!)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "core.wsgi:application"]