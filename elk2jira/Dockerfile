FROM python:3.8

WORKDIR /alerting

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY script.py .

CMD [ "python3", "./alert.py"]