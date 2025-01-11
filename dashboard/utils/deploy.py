
import os
import subprocess
import time
import shutil

# Конфигурация
PROJECT_NAME = "myproject"  # Замените на название вашего проекта
GITHUB_REPO = "https://github.com/your_username/your_repo.git"  # Замените на URL вашего репозитория
DOMAIN = "yourdomain.com"  # Замените на ваш домен
EMAIL = "your@email.com"  # Замените на ваш email для Let's Encrypt
DB_NAME = "django_db" # Замените на название вашей БД
DB_USER = "django_user"  # Замените на имя пользователя БД
DB_PASSWORD = "your_db_password"  # Замените на пароль пользователя БД
DOCKER_IMAGE_NAME = f"{PROJECT_NAME}-image"
DOCKER_CONTAINER_NAME = f"{PROJECT_NAME}-container"


def run_command(command, check=True):
    """Запускает команду в shell."""
    print(f"Running: {command}")
    try:
        subprocess.run(command, shell=True, check=check, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        exit(1)


def update_system():
    """Обновляет систему и устанавливает зависимости."""
    print("Updating system and installing dependencies...")
    run_command("sudo apt update -y")
    run_command("sudo apt upgrade -y")
    run_command("sudo apt install -y python3 python3-pip git docker.io docker-compose nginx mysql-server")
    run_command("sudo systemctl enable docker")
    run_command("sudo systemctl start docker")
    run_command("sudo systemctl enable nginx")


def clone_repo():
    """Клонирует репозиторий с GitHub."""
    print(f"Cloning repository from {GITHUB_REPO}...")
    run_command(f"git clone {GITHUB_REPO} {PROJECT_NAME}")
    os.chdir(PROJECT_NAME)


def create_virtualenv():
    """Создаёт виртуальное окружение и устанавливает зависимости."""
    print("Creating virtual environment and installing dependencies...")
    run_command("python3 -m venv venv")
    run_command("source venv/bin/activate && pip install -r requirements.txt")


def create_mysql_database():
    """Создает базу данных MySQL."""
    print("Creating MySQL database...")
    run_command(f"sudo mysql -e 'CREATE DATABASE IF NOT EXISTS {DB_NAME};'")
    run_command(f"sudo mysql -e \"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}';\"")
    run_command(f"sudo mysql -e \"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';\"")
    run_command("sudo mysql -e 'FLUSH PRIVILEGES;'")
    # Решение проблемы с утечкой памяти из-за логов mysql
    run_command("sudo sed -i 's/^max_connections/#max_connections/' /etc/mysql/mysql.conf.d/mysqld.cnf")
    run_command("sudo systemctl restart mysql")


def create_ssl_certificate():
    """Создает бесплатный SSL-сертификат с Let's Encrypt."""
    print("Creating SSL certificate with Let's Encrypt...")
    run_command("sudo apt install -y certbot python3-certbot-nginx")
    run_command(f"sudo certbot --nginx -d {DOMAIN} -m {EMAIL} --non-interactive --agree-tos")


def create_nginx_config():
    """Создает конфигурацию Nginx."""
    print("Creating Nginx configuration...")
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

    include /etc/nginx/snippets/ssl-params.conf;

    location / {{
        proxy_pass http://unix:/tmp/{PROJECT_NAME}.socket;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    location /static/ {{
        alias /home/ubuntu/{PROJECT_NAME}/static/;
    }}
}}
"""
    with open(f"/etc/nginx/sites-available/{PROJECT_NAME}", "w") as f:
        f.write(nginx_config)
    run_command(f"sudo ln -s /etc/nginx/sites-available/{PROJECT_NAME} /etc/nginx/sites-enabled/")
    run_command("sudo systemctl restart nginx")



def create_docker_files():
   """Создает Dockerfile и docker-compose.yml"""
   print("Creating Dockerfile and docker-compose.yml...")
   dockerfile_content = f"""
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8000
CMD ["gunicorn", "--bind", "unix:/tmp/{PROJECT_NAME}.socket",  "--workers=3", "{PROJECT_NAME}.wsgi:application"]
"""
   with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)


   docker_compose_content = f"""
version: "3.9"
services:
  web:
    build: .
    container_name: {DOCKER_CONTAINER_NAME}
    volumes:
      - .:/app
    restart: always
    """
   with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)

def build_docker_image():
  """Строит Docker образ."""
  print("Building Docker image...")
  run_command(f"docker build -t {DOCKER_IMAGE_NAME} .")

def run_docker_container():
   """Запускает Docker контейнер."""
   print("Running Docker container...")
   run_command("docker-compose up -d")

def create_systemd_service():
   """Создает systemd сервис."""
   print("Creating systemd service...")
   service_content = f"""
[Unit]
Description=Gunicorn daemon for {PROJECT_NAME}
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/{PROJECT_NAME}
ExecStart=/usr/bin/docker-compose up
ExecStop=/usr/bin/docker-compose down
Restart=always

[Install]
WantedBy=multi-user.target
"""
   with open(f"/etc/systemd/system/{PROJECT_NAME}.service", "w") as f:
       f.write(service_content)
   run_command(f"sudo systemctl daemon-reload")
   run_command(f"sudo systemctl enable {PROJECT_NAME}.service")
   run_command(f"sudo systemctl start {PROJECT_NAME}.service")

def collect_static():
   """Собирает статические файлы."""
   print("Collecting static files...")
   run_command("source venv/bin/activate && python manage.py collectstatic --noinput")

def migrate_db():
   """Мигрирует базу данных."""
   print("Migrating database...")
   run_command("source venv/bin/activate && python manage.py migrate")


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
    print("Deployment complete!")


if __name__ == "__main__":
    main()