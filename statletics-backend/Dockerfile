FROM python:3.13.2-slim

# Set the working directory
WORKDIR /app-backend

# Update package list and install build dependencies and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install the latest stable Rust toolchain via rustup (non-interactive install)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Cargo to PATH for subsequent commands
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy only the requirements file to leverage Docker caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port used by the backend (e.g., 8000)
EXPOSE 8000

# Command to start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
