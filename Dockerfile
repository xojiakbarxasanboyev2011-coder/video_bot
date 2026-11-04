FROM python:3.11-slim

# 1. Tizim paketlari
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 2. Deno (YouTube JavaScript himoyasi uchun)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /app

# 3. Python kutubxonalari (requirements.txt orqali curl_cffi<0.16 o'rnatiladi)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp[default,curl-cffi]" yt-dlp-ejs bgutil-ytdlp-pot-provider

# 4. PO Token Provider (Rust versiyasi - Node.js talab qilmaydi)
RUN curl -fsSL https://github.com/jim60105/bgutil-ytdlp-pot-provider-rs/releases/latest/download/bgutil-pot-linux-x86_64 -o /usr/local/bin/bgutil-pot && \
    chmod +x /usr/local/bin/bgutil-pot

# 5. Ishga tushirish skripti (POT server + bot)
RUN echo '#!/bin/bash\nbgutil-pot server --port 4416 &\nsleep 2\nexec python -m bot.main' > /app/start.sh && \
    chmod +x /app/start.sh

# 6. Qolgan fayllar
COPY . .

EXPOSE 10000
CMD ["/app/start.sh"]
