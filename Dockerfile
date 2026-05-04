FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
COPY app/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime Stage ---
FROM python:3.11-slim

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create user and group cleanly
RUN groupadd -r -g 1000 swiftuser && \
    useradd -r -u 1000 -g swiftuser -m -s /sbin/nologin swiftuser

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /root/.local /home/swiftuser/.local
COPY app/ .

# Ownership and Environment
RUN chown -R swiftuser:swiftuser /app /home/swiftuser/.local
ENV PATH=/home/swiftuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER swiftuser

# We don't hardcode EXPOSE to 3000 anymore to avoid confusion, 
# though Docker Compose will override this anyway.
EXPOSE 80 443 3000 5050 8080

# This is the ONLY CMD you need. 
# It triggers the if __name__ == "__main__": block in your main.py
CMD ["python", "main.py"]
