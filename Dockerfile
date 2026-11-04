FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Deno (YouTube JS himoyasi uchun)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /app

# Python kutubxonalari va YouTube PO Token plaginini o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp[default,curl-cffi]" yt-dlp-ejs bgutil-ytdlp-pot-provider

# PO Token serverini yuklash va ishga tushirish skriptini tayyorlash
RUN git clone --single-branch --branch 1.1.0 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /opt/bgutil && \
    cd /opt/bgutil/server && \
    npm install --production && \
    npx tsc

# Boshlash skripti: avval bgutil serverni ishga tushiramiz, keyin botni
RUN echo '#!/bin/bash\nnode /opt/bgutil/server/build/main.js &\nsleep 2\nexec python -m bot.main' > /app/start.sh && \
    chmod +x /app/start.sh

# Loyiha fayllari
COPY . .

EXPOSE 10000
CMD ["/app/start.sh"]
