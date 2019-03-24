FROM python:3.7-alpine
WORKDIR /firstapp
COPY . /firstapp

RUN python -m pip install -U -r requirements.txt
EXPOSE 8080
CMD ["python","restful_app.py"]
