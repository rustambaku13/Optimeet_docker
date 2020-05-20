FROM nginx 
RUN apt-get update && apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev  libncursesw5-dev xz-utils tk-dev vim
RUN wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
RUN tar xvf Python-3.8.2.tgz
WORKDIR Python-3.8.2
RUN ./configure
RUN make -j 8
RUN make altinstall
WORKDIR /
RUN apt-get install -y libpq-dev
EXPOSE 80 443
COPY Django/optify /optify
WORKDIR /optify
RUN pip3.8 install -r requirements.txt
RUN pip3.8 install supervisor
WORKDIR /etc/nginx/conf.d 
COPY default.conf default.conf
ENV db_url http://localhostblabla
WORKDIR /
COPY conf.d /etc/supervisor/conf.d 
COPY supervisord.conf /etc/supervisord.conf
