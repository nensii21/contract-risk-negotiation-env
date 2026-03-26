# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Run server
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "7860"]