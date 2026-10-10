# Start with the official NVIDIA CUDA 12.2.0 image as the base
FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04

# Set some environment variables to non-interactive (this prevents some prompts)
ENV DEBIAN_FRONTEND=non-interactive

# Install basic utilities and dependencies for Python build
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    build-essential \
    ca-certificates \
    software-properties-common \
    zlib1g-dev \
    libssl-dev \
    libreadline-dev \
    libsqlite3-dev \
    libbz2-dev \
    cmake \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python 3.11 from source
RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && \
    tar xzf Python-3.11.0.tgz && \
    cd Python-3.11.0 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.11.0.tgz Python-3.11.0

# Make Python 3.11 the default Python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1


# Add Poetry to PATH
ENV PATH="/root/.poetry/bin:${PATH}"

# Create a new user named llama
RUN useradd -ms /bin/bash llama
USER llama
WORKDIR /home/llama

# install llama-cpp
RUN \
    CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
    FORCE_CMAKE=1 pip install llama-cpp-python

# Expose any ports you need
# EXPOSE 8080

# Specify an entrypoint
# ENTRYPOINT ["./your_application"]
