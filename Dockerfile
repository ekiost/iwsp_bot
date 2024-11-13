FROM python:3.11-alpine
LABEL authors="ekiost"

# Create a working directory and copy the requirements file and bot.py
WORKDIR /app
COPY requirements.txt .
COPY bot.py .

# Install the required packages
RUN pip install -r requirements.txt

# Install necessary system packages
RUN apk add --no-cache firefox

# Install geckodriver
RUN apk add --no-cache geckodriver

# Run the bot
CMD ["python", "bot.py"]
