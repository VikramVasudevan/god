# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    GRADIO_ALLOW_FLAGGING=never \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=user . .

# Expose the port Streamlit runs on
EXPOSE 7860

# Command to run the application
# Hugging Face Spaces expect the app to run on port 7860
CMD ["streamlit", "run", "src/god_sim/app/streamlit_app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
