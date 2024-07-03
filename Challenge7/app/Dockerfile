FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  software-properties-common \
  git \
  && rm -rf /var/lib/apt/lists/*

# Create a virtualenv to keep dependencies together
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["chainlit", "run", "app.py",  "--host", "0.0.0.0",  "--port", "8080"]
