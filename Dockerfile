FROM python:3.11-slim

# Tizim paketlarini o'rnatish (ffmpeg, curl va unzip)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Deno o'rnatish (YouTube uchun JavaScript dvigateli)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Loyiha fayllarini ko'chirish
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir "yt-dlp[default,curl-cffi]"

COPY . .

# Render uchun port
EXPOSE 10000

# Botni ishga tushirish
CMD ["python", "-m", "bot.main"]
