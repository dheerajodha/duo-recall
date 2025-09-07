# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for Playwright browsers
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libfontconfig1 \
    libdbus-glib-1-2 \
    libgconf-2-4 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libxtst6 \
    libxss1 \
    libdrm2 \
    libgbm1 \
    libexpat1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libnspr4 \
    libfontconfig1 \
    libdbus-glib-1-2 \
    libgconf-2-4 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libxtst6 \
    libxss1 \
    libdrm2 \
    libgbm1 \
    libexpat1 \
    libxdamage1 \
    libxrandr2 \
    libxtst6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's browser binaries
RUN playwright install

# Copy the rest of the application's code
COPY . .

# Set a command to run when the container starts
CMD ["python", "duo_recall.py", "--help"]
