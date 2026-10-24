ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install runtime and build dependencies
RUN apk add --no-cache \
    git \
    bash \
    openssh-client \
    curl \
    libffi \
    libffi-dev \
    openssl \
    openssl-dev \
    build-base

WORKDIR /app

# Install python dependencies
COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8099

CMD [ "/run.sh" ]
