# ** info: declaration of the production image base version
FROM python:3.12.3-slim-bullseye

# ** info: copying the app requirements file from the testing image
COPY ["/requirements.txt","$WORKDIR/"]

# ** info: installing the dependencies and upgrading pip, wheel and setuptools
RUN pip install -r $WORKDIR/requirements.txt

# ** info: removing the app requirements file
RUN rm requirements.txt

# ** info: copying source code of the application from the testing image
COPY ["src", "$WORKDIR/src"]

# ** info: cleaning the python __pycache__ files
RUN find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

# ** info: adding support to es_CO.UTF-8 and en_US.UTF-8 locales
RUN apt-get update && apt-get install -y locales && rm -r /var/lib/apt/lists/*
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
RUN sed -i -e 's/# es_CO.UTF-8 UTF-8/es_CO.UTF-8 UTF-8/' /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales

# ** info: executing the app
ENTRYPOINT ["python", "src/credit_core_system.py"]
