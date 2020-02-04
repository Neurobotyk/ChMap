# FROM python:3.7
# RUN pip install pipenv
# COPY Pipfile* tmp/
# COPY . tmp/
# WORKDIR /tmp
# RUN ls
# RUN pipenv sync
# # RUN pipenv shell
# # RUN pip install /tmp/mysrc
# ENTRYPOINT pipenv run
# ENTRYPOINT python mysrc/app.py


# FROM python:3.7
# RUN pip install pipenv
# COPY Pipfile* tmp/
# RUN cd /tmp && pipenv lock --requirements > requirements.txt
# RUN pip install -r /tmp/requirements.txt
# RUN ls
# ENTRYPOINT ["python"]
# CMD ["app.py"]

FROM python:3.7
COPY . wrk/
RUN pip install pipenv
COPY Pipfile* wrk/
RUN cd wrk/ ; pipenv lock --requirements > requirements.txt
WORKDIR wrk/
RUN ls
RUN pip install -r requirements.txt
WORKDIR mysrc/
RUN ls
ENV LISTEN_PORT 5432
EXPOSE 5432
ENTRYPOINT ["python"]
CMD ["app.py"]