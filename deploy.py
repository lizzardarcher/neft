import os
import subprocess
import time

PROJECT_NAME = "neft"
GITHUB_REPO = "https://github.com/lizzardarcher/neft.git"
DOMAIN = "rusgeolog.ru"
EMAIL = "vodkinstorage@gmail.com"
DB_NAME = "django_db"
DB_USER = "django_user"
DB_PASSWORD = "k*hvcnUBcNN^g740kkkj8J&HVvcbk"
DOCKER_IMAGE_NAME = f"{PROJECT_NAME}-image"
DOCKER_CONTAINER_NAME = f"{PROJECT_NAME}-container"


def run_command(command, check=True):
    try:
        subprocess.run(command, shell=True, check=check, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        exit(1)


def update_system():
    os.system("sudo apt update -y")
    os.system("sudo apt upgrade -y")
    os.system("sudo apt install -y python3 python3-pip git docker.io docker-compose nginx mysql-server")
    os.system("sudo apt install -y python3.12-venv")
    os.system("sudo systemctl enable docker")
    os.system("sudo systemctl start docker")
    os.system("sudo systemctl enable nginx")


def clone_repo():
    os.system(f"git clone {GITHUB_REPO} {PROJECT_NAME}")
    os.chdir(PROJECT_NAME)


def create_virtualenv():
    os.system("python3 -m venv venv")
    os.system(f"source venv/bin/activate && pip install -r requirements.txt")


def create_mysql_database():
    os.system(f"sudo mysql -e 'CREATE DATABASE IF NOT EXISTS {DB_NAME};'")
    os.system(f"sudo mysql -e \"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}';\"")
    os.system(f"sudo mysql -e \"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';\"")
    os.system("sudo mysql -e 'FLUSH PRIVILEGES;'")


def create_ssl_certificate():
    os.system("sudo apt install -y certbot python3-certbot-nginx")
    os.system(f"sudo certbot --nginx -d {DOMAIN} -m {EMAIL} --non-interactive --agree-tos")


def create_nginx_config():
    nginx_config = f"""
server {{
    listen 80;
    server_name {DOMAIN};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {DOMAIN};

    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;

    include /etc/letsencrypt/options-ssl-nginx.conf;

    location / {{
        proxy_pass http://unix:/tmp/{PROJECT_NAME}.socket;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /static/ {{
        alias /opt/{PROJECT_NAME}/static/;
    }}

    location /media/ {{
        alias /opt/{PROJECT_NAME}/media/;
    }}
}}
"""
    with open(f"/etc/nginx/sites-available/{PROJECT_NAME}", "w") as f:
        f.write(nginx_config)
    os.system(f"sudo ln -s /etc/nginx/sites-available/{PROJECT_NAME} /etc/nginx/sites-enabled/")
    os.system("sudo systemctl restart nginx")


def create_docker_files():
    dockerfile_content = f"""
FROM python:3.12-slim
WORKDIR /{PROJECT_NAME}
COPY . /{PROJECT_NAME}
RUN python3 -m pip install -r requirements.txt
COPY . /{PROJECT_NAME}
EXPOSE 8000
CMD ["gunicorn", "--bind", "unix:/tmp/{PROJECT_NAME}.socket",  "--workers=5", "{PROJECT_NAME}.wsgi:application"]
"""
    with open(f"{PROJECT_NAME}/Dockerfile", "w") as f:
        f.write(dockerfile_content)

    docker_compose_content = f"""
version: "3.9"
services:
  web:
    build: .
    container_name: {DOCKER_CONTAINER_NAME}
    volumes:
      - .:/{PROJECT_NAME}
    restart: always
    """
    with open(f"{PROJECT_NAME}/docker-compose.yml", "w") as f:
        f.write(docker_compose_content)


def build_docker_image():
    os.chdir(f"/opt/{PROJECT_NAME}")
    os.system(f"docker build -t {DOCKER_IMAGE_NAME} .")


def run_docker_container():
    os.chdir(f"/opt/{PROJECT_NAME}")
    os.system("docker-compose up -d")


def create_systemd_service():
    service_content = f"""
[Unit]
Description=Gunicorn daemon for {PROJECT_NAME}
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/{PROJECT_NAME}
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always

[Install]
WantedBy=multi-user.target
"""
    with open(f"/etc/systemd/system/{PROJECT_NAME}.service", "w") as f:
        f.write(service_content)
    os.system(f"sudo systemctl daemon-reload")
    os.system(f"sudo systemctl enable {PROJECT_NAME}.service")
    os.system(f"sudo systemctl start {PROJECT_NAME}.service")


def collect_static():
    os.system(f"source venv/bin/activate && python3 manage.py collectstatic --noinput")


def migrate_db():
    os.system(f"source venv/bin/activate && python3 manage.py migrate")


def main():
    update_system()
    clone_repo()
    create_virtualenv()
    create_mysql_database()
    create_ssl_certificate()
    create_nginx_config()
    create_docker_files()
    build_docker_image()
    run_docker_container()
    collect_static()
    migrate_db()
    create_systemd_service()

if __name__ == "__main__":
    main()