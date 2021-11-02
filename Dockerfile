FROM python:3

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY start.py /app/start.py
COPY qbittorrent.py /app/qbittorrent.py

ENTRYPOINT ["python3", "/app/start.py"]