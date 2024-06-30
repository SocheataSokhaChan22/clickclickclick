FROM selenium/standalone-chrome:latest

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    chromium \
    chromium-driver \
    wget \
    unzip \
    gnupg

# Upgrade pip
RUN pip3 install --upgrade pip

# Set environment variables
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/lib/chromium-browser/
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV CHROME_DRIVER_PATH=/usr/local/bin/chromedriver
ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Copy the Streamlit app
COPY . /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit runs on
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py"]
