FROM python:3.7.2-alpine3.8

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY dockerdist .

CMD [ "python", "./main.py" ]