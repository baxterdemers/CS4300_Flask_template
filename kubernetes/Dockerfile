# Read from Ubuntu Base Image
FROM python:3.6.8
RUN mkdir -p /service
# Copy over all the files of interest
ADD app /service/app
ADD app.py /service/app.py
ADD config.py /service/config.py
ADD manage.py /service/manage.py
ADD get_names.py /service/get_names.py
ADD requirements.txt /service/requirements.txt
WORKDIR /service/
RUN pip install -r requirements.txt
RUN python -m nltk.downloader all
CMD python -u app.py $APP_SETTINGS $DATABASE_URL
