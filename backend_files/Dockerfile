# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend files (app.py, requirements.txt, superkart_model.joblib) into the container
COPY . .

# Install the Python dependencies without caching to keep the image size minimal
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 7860 to the outside world
EXPOSE 7860

# Start the application using Gunicorn (a production-grade WSGI HTTP server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
