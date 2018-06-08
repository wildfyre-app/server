FROM python:3.6-slim

WORKDIR /src
ADD api /src

RUN pip install --no-cache-dir -r requirements.txt \
  && pip install --no-cache-dir gunicorn \
  && python manage.py test \
  && mv production.dist.py production.py

EXPOSE 80

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:80", "api.wsgi"]
