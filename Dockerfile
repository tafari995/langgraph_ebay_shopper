
FROM python:3.12-slim-bookworm

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#RUN useradd --create-home --shell /bin/bash appuser && \
#    chown -R appuser:appuser /langgraph_ebay_shopper

#USER appuser

CMD ["python","./graph_deQwen.py"]