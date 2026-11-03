FROM python:3.11-slim

# Tizim paketlari
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Deno (YouTube JS himoyasi uchun)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /app

# Python kutubxonalari va YouTube PO Token provayderi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp[default,curl-cffi]" yt-dlp-ejs bgutil-ytdlp-pot-provider

# Loyiha fayllari
COPY . .

EXPOSE 10000
CMD ["python", "-m", "bot.main"]
