import os
import subprocess
import time
import shutil

# Конфигурация
PROJECT_NAME = "neft"
GITHUB_REPO = "https://github.com/lizzardarcher/neft.git"
DOMAIN = "rusgeolog.ru"
EMAIL = "vodkinstorage@gmail.com"
DB_NAME = "django_db"
DB_USER = "django_user"
DB_PASSWORD = "k*hvcnUBcNN^g740kkkj8J&HVvcbk"
DOCKER_IMAGE_NAME = f"{PROJECT_NAME}-image"
DOCKER_CONTAINER_NAME = f"{PROJECT_NAME}-container"
WORK_DIR = "/opt"
USER = 'root'

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
    os.system("sudo apt update -y")
    os.system("sudo apt upgrade -y")
    os.system("sudo apt install -y python3 python3-pip git nginx mysql-server")
    os.system("sudo apt install -y python3.12-venv")
    os.system("sudo systemctl enable nginx")


def clone_repo():
    """Клонирует репозиторий с GitHub."""
    print(f"Cloning repository from {GITHUB_REPO}...")
    os.system(f"git clone {GITHUB_REPO} {PROJECT_NAME}")
    os.chdir(PROJECT_NAME)


def create_virtualenv():
    """Создаёт виртуальное окружение и устанавливает зависимости."""
    print("Creating virtual environment and installing dependencies...")
    os.chdir(f"{WORK_DIR}/{PROJECT_NAME}")
    os.system("python3 -m venv venv")
    os.system(f"source venv/bin/activate && pip install -r requirements.txt")


def create_mysql_database():
    """Создает базу данных MySQL."""
    print("Creating MySQL database...")
    os.system(f"sudo mysql -e 'CREATE DATABASE IF NOT EXISTS {DB_NAME};'")
    os.system(f"sudo mysql -e \"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}';\"")
    os.system(f"sudo mysql -e \"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';\"")
    os.system("sudo mysql -e 'FLUSH PRIVILEGES;'")


def create_ssl_certificate():
    """Создает бесплатный SSL-сертификат с Let's Encrypt."""
    print("Creating SSL certificate with Let's Encrypt...")
    os.system("sudo apt install -y certbot python3-certbot-nginx")
    os.system(f"sudo certbot --nginx -d {DOMAIN} -m {EMAIL} --non-interactive --agree-tos")


def create_gunicorn_service():
    """Создает сервис systemd для Gunicorn."""
    gunicorn_cmd = f"/opt/{PROJECT_NAME}/venv/bin/gunicorn -c gunicorn-cfg.py {PROJECT_NAME}.wsgi:application"  # Предполагает наличие wsgi файла
    service_file = f"""
[Unit]
Description=Gunicorn service for {PROJECT_NAME}
Requires={PROJECT_NAME}-gunicorn.socket
After=network.target

[Service]
Type=notify
NotifyAccess=main
User={USER}
RuntimeDirectory=gunicorn
WorkingDirectory=/opt/{PROJECT_NAME}
Environment="PYTHONPATH=/opt/{PROJECT_NAME}"
ExecStart={gunicorn_cmd}
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    with open(f"/etc/systemd/system/{PROJECT_NAME}-gunicorn.service", "w") as f:
        f.write(service_file)
    os.system("systemctl daemon-reload")
    os.system(f"systemctl enable {PROJECT_NAME}-gunicorn.service")
    os.system(f"systemctl start {PROJECT_NAME}-gunicorn.service")


def create_gunicorn_socket():
    """Создает сокет systemd для Gunicorn."""
    socket_file = f"""
[Unit]
Description=gunicorn socket for {PROJECT_NAME}

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
"""
    with open(f"/etc/systemd/system/{PROJECT_NAME}-gunicorn.socket", "w") as f:
        f.write(socket_file)
    os.system("systemctl daemon-reload")
    os.system(f"systemctl enable {PROJECT_NAME}-gunicorn.socket")
    os.system(f"systemctl start {PROJECT_NAME}-gunicorn.socket")


def create_nginx_config():
    """Создает конфигурацию Nginx."""
    print("Creating Nginx configuration...")
    nginx_config = f"""
server {{
    listen 80;
    server_name {DOMAIN};
    # return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {DOMAIN};

    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;

    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    client_max_body_size 1G;
    
    location / {{
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # proxy_set_header X-Forwarded-Proto $scheme;
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


def collect_static():
    """Собирает статические файлы."""
    print("Collecting static files...")
    os.chdir(f"{WORK_DIR}/{PROJECT_NAME}")
    os.system(f"source venv/bin/activate && python3 manage.py collectstatic --noinput")


def migrate_db():
    """Мигрирует базу данных."""
    print("Migrating database...")
    os.chdir(f"{WORK_DIR}/{PROJECT_NAME}")
    os.system(f"source venv/bin/activate && python3 manage.py migrate")


def main():
    update_system()

    clone_repo()

    create_virtualenv()

    create_mysql_database()

    create_ssl_certificate()

    create_gunicorn_service()

    create_gunicorn_socket()

    create_nginx_config()

    collect_static()

    migrate_db()

    print("Deployment complete!")


if __name__ == "__main__":
    main()