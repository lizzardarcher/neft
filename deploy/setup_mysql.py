import subprocess

def install_mysql():
    """
    Устанавливает MySQL на систему.
    """
    try:
        subprocess.check_call(["apt-get", "update"])
        subprocess.check_call(["apt-get", "install", "-y", "mysql-server"])
        print("MySQL успешно установлен!")
    except subprocess.CalledProcessError:
        print("Ошибка при установке MySQL. Проверьте права доступа и подключение к интернету.")

def create_database(database_name):
    """
    Создает базу данных с указанным именем.
    """
    try:
        subprocess.check_call(["mysql", "-u", "root", "-e", f"CREATE DATABASE {database_name};"])
        print(f"База данных {database_name} успешно создана!")
    except subprocess.CalledProcessError:
        print(f"Ошибка при создании базы данных {database_name}. Проверьте права доступа и имя базы данных.")

def create_user(username, password):
    """
    Создает нового пользователя с указанным именем и паролем с правами администратора.
    """
    try:
        subprocess.check_call(["mysql", "-u", "root", "-e", f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';"])
        subprocess.check_call(["mysql", "-u", "root", "-e", f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'localhost';"])
        print(f"Пользователь {username} успешно создан с полными правами!")
    except subprocess.CalledProcessError:
        print(f"Ошибка при создании пользователя {username}. Проверьте права доступа.")

if __name__ == "__main__":
    install_mysql()

    database_name = input("Введите имя базы данных: ")
    create_database(database_name)

    username = input("Введите имя пользователя: ")
    password = input("Введите пароль для пользователя: ")
    create_user(username, password)