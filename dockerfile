FROM python:3.11.3
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN playwright install --with-deps chromium
CMD ["python", "pixiv.py"]