FROM python:3.9.18-slim-bullseye
LABEL Maintainer="OsmanKandemir"
COPY . /app
WORKDIR /app
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip --no-cache-dir install -r requirements.txt
ENTRYPOINT ["python", "generator.py"]


#docker build -t webwordlistgenerator .
#docker run webwordlistgenerator --domains target-web.com target-web2.com
