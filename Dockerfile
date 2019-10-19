FROM python:3.7

# Set environment variables

# Log messages will be immediately dumped to
# the standard output stream instead of being buffered
ENV PYTHONUNBUFFERED 1

# Add support for TZ
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN sed -i 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y tzdata vim
RUN rm -rf /var/cache/apk/*

# Copy dependencies file
COPY requirements.txt /

# Install dependencies
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /requirements.txt

# Copy health checker
COPY wait-for-it.sh /

# COPY uwsgi config file
COPY uwsgi.ini /

# Copy project
COPY . /

# Create touch-reload file
RUN touch /uwsgi-touch-reload

WORKDIR /