FROM python:3.11-slim

# Kerakli tizim paketlarini o'rnatish
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Deno (JavaScript dvigateli) o'rnatish
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Python muhitini sozlash
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "yt-dlp[default,curl-cffi]" yt-dlp-ejs

# Qolgan fayllarni ko'chirish
COPY . .

# Render uchun port
EXPOSE 10000

# Botni ishga tushirish
CMD ["python", "-m", "bot.main"]
