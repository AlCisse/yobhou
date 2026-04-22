FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libglx-mesa0 \
    swig \
    libfreetype6 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyMuPDF first (with binary wheel)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PyMuPDF==1.27.2.2

# Install other base packages
RUN pip install --no-cache-dir Django==5.0.6 djangorestframework==3.15.1 djangorestframework-simplejwt==5.3.1 gunicorn==21.2.0 && \
    pip install --no-cache-dir psycopg2-binary==2.9.9 redis==5.0.1 elasticsearch==8.11.0 elasticsearch-dsl==8.11.0 && \
    pip install --no-cache-dir cryptography==41.0.7 python-dotenv==1.0.0 && \
    pip install --no-cache-dir pytest==8.2.0 pytest-django==4.8.0 factory-boy==3.2.1 black==24.4.0 pylint==3.1.0 pyclipper==1.3.0.post4 lmdb==1.4.1 requests==2.31.0 tqdm==4.66.1 babel==2.14.0 pyyaml==6.0.1 && \
    pip install --no-cache-dir paddlepaddle==2.6.2 Pillow==10.0.1 && \
    pip install --no-cache-dir opencv-python==4.6.0.66 --no-deps && \
    pip install --no-cache-dir shapely==2.0.1 scikit-image==0.21.0 imgaug==0.4.0 --no-deps && \
    pip install --no-cache-dir paddleocr==2.7.0 --no-deps && \
    pip install --no-cache-dir attrdict==2.0.1 visualdl==2.5.3 premailer==3.10.0 flask==3.0.0 fire==0.5.0 beautifulsoup4==4.12.0 openpyxl==3.1.2 python-docx==0.8.11 pdf2docx==0.5.8 rapidfuzz==3.0.0 cython==3.0.0 imageio==2.31.0 lazy_loader==0.3 networkx==3.1 PyWavelets==1.4.1 scipy==1.11.1 tifffile==2023.7.10 && \
    pip install --no-cache-dir numpy==1.24.3

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