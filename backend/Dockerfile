FROM node:22-alpine AS frontend-builder
WORKDIR /build
COPY frontend/ .
RUN npm install
RUN npm run build
# Export the Next.js app as static files
RUN npm run export
# The export command creates an "out" directory with static HTML/CSS/JS
RUN cp -r out frontend-out

FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
COPY --from=frontend-builder /build/frontend-out public/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
