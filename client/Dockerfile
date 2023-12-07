FROM python:3.10.13

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/client
RUN ["chmod", "+x", "/app/client/run_client.sh"]