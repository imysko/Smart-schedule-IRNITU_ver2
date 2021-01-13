FROM python:3.8

RUN mkdir -p /usr/src/getting_schedule/
WORKDIR /usr/src/getting_schedule/


COPY . /usr/src/getting_schedule/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]