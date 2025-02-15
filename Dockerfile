# Use Python 3.13 as the base image
FROM python:3.13

# Set working directory
WORKDIR /app

# Install Node.js, npm,jq and including e2fsprogs,acl for managing Access Control Lists
RUN apt update && apt install -y curl e2fsprogs acl jq tesseract-ocr vim  \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt install -y nodejs


# Verify Node.js and npm installation
RUN node -v
RUN npm -v

# Install Prettier globally
RUN npm install -g prettier@3.4.2

# Install Python dependencies (one per line)
RUN pip install uv
RUN pip install pillow
RUN pip install faker
RUN pip install uvicorn
RUN pip install fastapi
RUN pip install openapi
RUN pip install pydantic
RUN pip install requests
RUN pip install python-git
RUN pip install numpy
RUN pip install pandas
RUN pip install matplotlib
RUN pip install scikit-learn
RUN pip install gitpython 
RUN pip install duckdb 
RUN pip install beautifulsoup4 
RUN pip install speechrecognition 
RUN pip install whisper 
RUN pip install markdown 
RUN pip install flask 
RUN pip install pytesseract 
RUN pip install openai==0.28  # Install the openai package

# Copy project files
COPY . /app

# Create /data directory and set permissions
RUN mkdir -p /data
RUN chmod 777 /data


# Apply chattr +a to /data so files can be created/modified but not deleted
# cant do in dockerfile, docker doesnt like it ; ) . So do it in entrypoint
# RUN chattr +a /data

# Set environment variable
ENV AIPROXY_TOKEN=""


# Set up entrypoint Python script
COPY entrypoint.py /entrypoint.py
COPY main.py /main.py

# Default command to run FastAPI
CMD ["python", "/entrypoint.py"]