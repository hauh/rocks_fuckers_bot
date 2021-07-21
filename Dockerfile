FROM python:slim
WORKDIR /opt/template_bot/
ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt
COPY bot ./bot
CMD ["python", "-m", "bot"]
