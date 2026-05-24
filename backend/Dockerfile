# Multi-stage Docker build for the PM MVP.
# Stage 1 – Build the Next.js frontend using Node.
FROM node:22-alpine AS frontend-builder
WORKDIR /app
COPY frontend/ .
RUN npm install
RUN npm run build

# Stage 2 – Runtime image based on Python, with Node installed for the Next.js server.
FROM python:3.11-slim
WORKDIR /app
# Install Node.js and npm (required to run the Next.js server).
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && rm -rf /var/lib/apt/lists/*
# Copy backend source code.
COPY backend/ .
# Install Python dependencies.
RUN pip install --upgrade pip && pip install -r requirements.txt
# Copy the built frontend assets and Node modules from the builder stage.
COPY --from=frontend-builder /app/.next .next
COPY --from=frontend-builder /app/public public
COPY --from=frontend-builder /app/package.json .
COPY --from=frontend-builder /app/node_modules node_modules
# Expose FastAPI (8000) and Next.js (3000) ports.
EXPOSE 8000 3000
# Run both services concurrently (for demo purposes).
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & npm start"]