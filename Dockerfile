
FROM python:3.12-slim-bookworm

ENV PORT=8000

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash --user-group appuser && \
    chown -R appuser:appuser /usr/src/app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose the port (important for Fly.io)
EXPOSE 8000


CMD ["python","./app.py"]

