# Use the official Python image.
FROM python:3.12-slim

# Set the working directory.
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the project files.
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
COPY app.py app.py
COPY credentials.json credentials.json
COPY token.json token.json

RUN apt-get update && apt-get install -y build-essential

# Install dependencies.
RUN uv pip install --no-cache --system -r pyproject.toml

# Set the command to run the application.
CMD ["python", "app.py"]
