FROM python:3.8

RUN mkdir -p /usr/src/parser/
WORKDIR /usr/src/parser/


COPY . /usr/src/parser/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "parser.py"]