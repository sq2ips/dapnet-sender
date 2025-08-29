FROM python:3

WORKDIR /usr/src/dapnet-sender

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./dapnet.py .
COPY ./utils.py .
RUN mkdir modules
COPY ./modules/* ./modules/

CMD [ "python", "./dapnet.py" ]