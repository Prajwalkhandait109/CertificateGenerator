FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p uploads output

# Expose port for the Flask app
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]