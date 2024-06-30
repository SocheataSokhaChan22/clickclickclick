FROM python:3.9-slim

# Install Chrome and other dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && apt-get install -y libnss3 libgconf-2-4 libxss1 libappindicator1 libindicator7 \
    && apt-get install -y fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libexpat1 libgbm1 libgtk-3-0 libnspr4 libpango-1.0-0 libxcomposite1 libxrandr2 xdg-utils libu2f-udev libvulkan1 libxshmfence1 \
    && apt-get install -y --no-install-recommends chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Set environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/local/bin/chromedriver

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . /app
WORKDIR /app

# Expose the port Streamlit runs on
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py"]
