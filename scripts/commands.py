import asyncio
import os
import platform
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import asyncpg
import uvicorn

from app.core.dependencies import database_client, get_db_session
from app.core.security.password import pwd_context
from app.models import User


class DockerDaemonNotRunningError(Exception):
    def __init__(self, message=None):
        self.message = (
            message
            or "Docker демон не запущен. Убедись, что Docker Desktop запущен и работает."
        )
        super().__init__(self.message)


class DockerContainerConflictError(Exception):
    def __init__(self, container_name=None, message=None):
        if container_name:
            self.message = (
                message
                or f"Конфликт имен контейнеров. Контейнер '{container_name}' уже используется. Удали его или переименуй."
            )
        else:
            self.message = (
                message
                or "Конфликт имен контейнеров. Удали существующий контейнер или переименуй его."
            )
        super().__init__(self.message)


TEST_ENV_FILE = ".env.test"
DEV_ENV_FILE = ".env.dev"
ROOT_DIR = Path(__file__).parents[1]

COMPOSE_FILE_WITHOUT_BACKEND = "docker-compose.dev.yml"

DEFAULT_PORTS = {
    "FASTAPI": 8000,
    "RABBITMQ": 5672,
    "RABBITMQ_UI": 15672,
    "POSTGRES": 5432,
    "REDIS": 6380,
    "PGADMIN": 5050,
    "REDIS_COMMANDER": 8081,
}


def load_env_vars(env_file_path: str = None) -> dict:
    if env_file_path is None:
        dev_env_path = ROOT_DIR / DEV_ENV_FILE
        test_env_path = ROOT_DIR / TEST_ENV_FILE

        if dev_env_path.exists():
            env_file_path = str(dev_env_path)
            print(f"📋 Используем dev конфигурацию: {DEV_ENV_FILE}")
        elif test_env_path.exists():
            env_file_path = str(test_env_path)
            print(f"📋 Используем тестовую конфигурацию: {TEST_ENV_FILE}")
        else:
            print("❌ Не найден файл конфигурации (.env.dev или .env.test)")
            return {}

    env_vars = {}
    if os.path.exists(env_file_path):
        with open(env_file_path, encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        value = value.strip("\"'")
                        env_vars[key] = value
                    except ValueError:
                        pass
    else:
        print(f"❌ Файл конфигурации не найден: {env_file_path}")

    return env_vars


def run_compose_command(
    command: str | list,
    compose_file: str = COMPOSE_FILE_WITHOUT_BACKEND,
    env: dict = None,
) -> None:
    if isinstance(command, str):
        command = command.split()

    compose_path = os.path.join(ROOT_DIR, compose_file)
    if not os.path.exists(compose_path):
        print(f"❌ Файл {compose_file} не найден в директории {ROOT_DIR}")
        raise FileNotFoundError(f"❌ Файл {compose_file} не найден в {ROOT_DIR}")

    env_path = os.path.join(ROOT_DIR, DEV_ENV_FILE)
    if not os.path.exists(env_path):
        print(f"❌ Файл {DEV_ENV_FILE} не найден в директории {ROOT_DIR}")
        print("💡 Создайте файл .env.dev с необходимыми переменными окружения")
        raise FileNotFoundError(
            f"❌ Файл {DEV_ENV_FILE} не найден. Создайте его перед запуском."
        )

    environment = os.environ.copy()
    environment.update(load_env_vars())
    if env:
        environment.update(env)

    # show_output = any(cmd in command for cmd in ['up', 'build'])

    try:
        subprocess.run(
            ["docker-compose", "-f", compose_file] + command,
            cwd=ROOT_DIR,
            check=True,
            env=environment,
            # capture_output=not show_output,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        if (
            "docker daemon is not running" in error_output
            or "pipe/docker_engine" in error_output
        ):
            raise DockerDaemonNotRunningError() from e
        elif (
            "Conflict" in error_output
            and "is already in use by container" in error_output
        ):
            import re

            container_match = re.search(r'The container name "([^"]+)"', error_output)
            container_name = container_match.group(1) if container_match else None
            raise DockerContainerConflictError(container_name) from e
        raise


def find_free_port(start_port: int = 8000) -> int:
    port = start_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("Нет свободных портов! Ахуеть!")


def get_available_port(default_port: int) -> int:
    port = default_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"Не могу найти свободный порт после {default_port}")


def is_port_free(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", port))
            return True
    except OSError:
        return False


def get_port(service: str) -> int:
    service_upper = service.upper().replace("_PORT", "")
    return int(os.getenv(service, DEFAULT_PORTS[service_upper]))


def show_loader(message: str, stop_event: threading.Event):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{chars[i % len(chars)]} {message}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    sys.stdout.flush()


def check_service(name: str, port: int, retries: int = 10, delay: int = 3) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(retries):
        try:
            sock.connect(("localhost", port))
            sock.close()
            return True
        except:
            print(f"⏳ Ждём {name} на порту {port}...")
            time.sleep(delay)
    return False


def check_services():
    services_config = {
        "Redis": ("REDIS_PORT", 5),
        "RabbitMQ": ("RABBITMQ_UI_PORT", 20),
        "PostgreSQL": ("POSTGRES_PORT", 30),
    }

    for service_name, (port_key, retries) in services_config.items():
        port = get_port(port_key)
        if not check_service(service_name, port, retries):
            print(f"❌ {service_name} не доступен на порту {port}!")
            return False
    return True


def get_postgres_container_name() -> str:
    try:
        which_result = subprocess.run(
            ["which", "docker"], capture_output=True, text=True
        )
        if which_result.returncode != 0:
            print("ℹ️ Docker не найден, используем прямое подключение к PostgreSQL")
            return "postgres"

        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        containers = [name for name in result.stdout.strip().split("\n") if name]
        if not containers:
            print(
                "⚠️ Контейнер PostgreSQL не найден через Docker, используем прямое подключение"
            )
            return "postgres"
        return containers[0]
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Ошибка при поиске контейнера PostgreSQL через Docker: {e}")
        return "postgres"
    except Exception as e:
        print(f"⚠️ Непредвиденная ошибка: {e}")
        return "postgres"


def create_database():
    print("🛠️ Проверяем наличие базы данных...")

    db_config = load_env_vars()

    postgres_container = get_postgres_container_name()
    print(f"🔍 Используем PostgreSQL: {postgres_container}")

    user = db_config.get("POSTGRES_USER", "postgres")
    password = db_config.get("POSTGRES_PASSWORD", "")
    host = db_config.get("POSTGRES_HOST", "localhost")
    port = db_config.get("POSTGRES_PORT", "5432")
    db_name = db_config.get("POSTGRES_DB", "aichat_db")

    try:
        which_docker = subprocess.run(["which", "docker"], capture_output=True)
        docker_available = which_docker.returncode == 0

        if docker_available:
            check_db_inside = subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    postgres_container,
                    "psql",
                    "-U",
                    user,
                    "-c",
                    f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';",
                ],
                capture_output=True,
                text=True,
            )

            if "1 row" not in check_db_inside.stdout:
                print(
                    f"🛠️ База данных {db_name} не найдена внутри контейнера, создаём..."
                )
                create_cmd = [
                    "docker",
                    "exec",
                    "-i",
                    postgres_container,
                    "psql",
                    "-U",
                    user,
                    "-c",
                    f"CREATE DATABASE {db_name};",
                ]
                subprocess.run(create_cmd, check=True)
                print(f"✅ База данных {db_name} создана внутри контейнера!")
            else:
                print(f"✅ База данных {db_name} существует внутри контейнера!")
        else:
            print(f"🔄 Проверяем БД напрямую через psql...")

            psql_command = f"psql -U {user} -h {host} -p {port}"
            if password:
                env = os.environ.copy()
                env["PGPASSWORD"] = password
            else:
                env = os.environ.copy()

            check_db = subprocess.run(
                f"{psql_command} -c \"SELECT 1 FROM pg_database WHERE datname = '{db_name}';\"",
                shell=True,
                env=env,
                capture_output=True,
                text=True,
            )

            if "1 row" not in check_db.stdout:
                print(f"🛠️ База данных {db_name} не найдена, создаём...")
                create_cmd = f'{psql_command} -c "CREATE DATABASE {db_name};"'
                subprocess.run(create_cmd, shell=True, env=env, check=True)
                print(f"✅ База данных {db_name} создана!")
            else:
                print(f"✅ База данных {db_name} существует!")

        dsn = f"postgresql://{user}:*******@{host}:{port}/{db_name}"
        print(f"🔄 Информация о подключении к БД: {dsn} (пароль скрыт)")

        return True
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        return False


def start_infrastructure():
    print("🚀 Запускаем инфраструктуру...")

    env_vars = load_env_vars()

    busy_ports = []
    for service, default_port in DEFAULT_PORTS.items():
        port = int(env_vars.get(f"{service}_PORT", default_port))
        if not is_port_free(port):
            busy_ports.append(f"{service}: {port}")

    if busy_ports:
        print("❌ Следующие порты заняты:")
        for port_info in busy_ports:
            print(f"   - {port_info}")
        print("💡 Останови процессы на этих портах или измени порты в .env.dev")
        return False

    try:
        try:
            docker_info = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, check=True
            )
            print("✅ Docker запущен и работает")
        except subprocess.CalledProcessError as e:
            print("❌ Проблема с Docker:")
            if "permission denied" in str(e.stderr).lower():
                print(
                    "💡 Нет прав доступа к Docker. Попробуйте запустить от администратора."
                )
            elif "cannot connect to the docker daemon" in str(e.stderr).lower():
                print("💡 Docker Daemon не отвечает. Проверьте что:")
                print("   1. Docker Desktop точно запущен")
                print("   2. Служба Docker Engine работает")
                print("   3. Нет конфликтов с WSL или другими службами")
            raise DockerDaemonNotRunningError()

        print("🔍 Проверяем запущенные контейнеры...")
        ps_result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        if ps_result.stdout.strip():
            print("⚠️ Найдены запущенные контейнеры:")
            for container in ps_result.stdout.strip().split("\n"):
                print(f"   - {container}")

        try:
            run_compose_command("down --remove-orphans")
        except subprocess.CalledProcessError as e:
            error_output = str(e)
            if (
                "docker daemon is not running" in error_output
                or "pipe/docker_engine" in error_output
            ):
                raise DockerDaemonNotRunningError()
            raise

        try:
            subprocess.run(["docker", "volume", "prune", "-f"], check=True)
        except subprocess.CalledProcessError as e:
            error_output = str(e)
            if (
                "docker daemon is not running" in error_output
                or "pipe/docker_engine" in error_output
            ):
                raise DockerDaemonNotRunningError()
            raise

        ports = {
            service: get_available_port(default_port)
            for service, default_port in DEFAULT_PORTS.items()
        }

        env = {f"{service}_PORT": str(port) for service, port in ports.items()}
        stop_loader = threading.Event()
        loader_thread = threading.Thread(target=show_loader, args=("", stop_loader))
        loader_thread.start()

        try:
            run_compose_command(["up", "-d"], COMPOSE_FILE_WITHOUT_BACKEND, env=env)
        except subprocess.CalledProcessError as e:
            error_output = str(e)
            if (
                "docker daemon is not running" in error_output
                or "pipe/docker_engine" in error_output
            ):
                raise DockerDaemonNotRunningError()
            elif (
                "Conflict" in error_output
                and "is already in use by container" in error_output
            ):
                import re

                container_match = re.search(
                    r'The container name "([^"]+)"', error_output
                )
                container_name = container_match.group(1) if container_match else None
                raise DockerContainerConflictError(container_name)
            raise
        finally:
            stop_loader.set()
            loader_thread.join()
            print("✅ Контейнеры запущены!")

        check_services()

        print("📦 Запускаем миграции...")
        migrate()
        print("✅ Миграции выполнены!")

        print("\n" + "=" * 60)
        print("🎯 ИНФРАСТРУКТУРА ГОТОВА")
        print("=" * 60)

        print("\n📡 СЕРВИСЫ:")
        print(f"📊 FastAPI Swagger:    http://localhost:{ports['FASTAPI']}/docs")
        print(f"🐰 RabbitMQ:       http://localhost:{ports['RABBITMQ_UI']}")
        print(f"🗄️ PostgreSQL:        localhost:{ports['POSTGRES']}")
        print(f"📦 Redis:             localhost:{ports['REDIS']}")

        print("\n🔧 АДМИН ПАНЕЛИ:")
        print(f"🔍 PgAdmin:           http://localhost:{ports['PGADMIN']}")
        print(f"📊 Redis Commander:    http://localhost:{ports['REDIS_COMMANDER']}")

        print("\n🔑 ДОСТУПЫ:")
        print(
            f"🔍 PgAdmin:           {env_vars.get('PGADMIN_DEFAULT_EMAIL', 'admin@admin.com')} / {env_vars.get('PGADMIN_DEFAULT_PASSWORD', 'admin')}"
        )
        print(
            f"🐰 RabbitMQ:          {env_vars.get('RABBITMQ_USER', 'guest')} / {env_vars.get('RABBITMQ_PASS', 'guest')}"
        )
        print(
            f"🗄️ PostgreSQL:        {env_vars.get('POSTGRES_USER', 'postgres')} / {env_vars.get('POSTGRES_PASSWORD', 'postgres')}"
        )

        return True
    except DockerDaemonNotRunningError as e:
        print(f"❌ {e}")
        print("💡 Запусти Docker Desktop и попробуй снова, олух.")
        return False
    except DockerContainerConflictError as e:
        print(f"❌ {e}")
        print("💡 Выполни следующую команду для удаления конфликтующих контейнеров:")
        print("```")
        print("docker rm -f $(docker ps -aq)")
        print("```")
        return False
    except Exception as e:
        print(f"❌ Ошибка при запуске инфраструктуры: {e}")
        return False


def setup():
    system = platform.system()
    if system == "Windows":
        subprocess.run(["powershell", "-File", "scripts/setup.ps1"], check=True)
    else:
        subprocess.run(["bash", "scripts/setup.sh"], check=True)


def activate():
    system = platform.system()
    if system == "Windows":
        subprocess.run(["powershell", "-File", "scripts/activate.ps1"], check=True)
    else:
        subprocess.run(["bash", "scripts/activate.sh"], check=True)


def dev(port: Optional[int] = None):
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))

    if not start_infrastructure():
        return

    if port is None:
        port = find_free_port()

    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК FASTAPI СЕРВЕРА")
    print("=" * 60)
    print(f"🌐 Адрес: http://localhost:{port}")
    print(f"📚 Документация: http://localhost:{port}/docs")
    print(f"🔄 Hot Reload: включён")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="debug",
        access_log=False,
    )


def serve(port: Optional[int] = None):
    if port is None:
        port = find_free_port()

    print(f"🚀 Запускаем сервер на порту {port}")
    subprocess.run(
        [
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--proxy-headers",
            "--forwarded-allow-ips=*",
        ],
        check=True,
    )


def migrate():
    subprocess.run(["alembic", "upgrade", "head"], check=True)


async def create_superuser():
    await database_client.connect()

    session_gen = get_db_session()
    session = await anext(session_gen)
    try:
        username = input("Enter username: ")
        first_name = input("Enter first_name: ")
        last_name = input("Enter last_name: ")
        email = input("Enter email: ")
        password = input("Enter password: ")

        hashed_password = pwd_context.hash(password)

        superuser = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            is_verified=True,
            is_superuser=True,
        )
        session.add(superuser)
        await session.commit()
        print(f"✅ Superuser '{username}' успешно создан!")
    finally:
        await session_gen.aclose()
        await database_client.close()


def run_create_superuser():
    asyncio.run(create_superuser())


def test(
    path: str = "tests/",
    marker: str = None,
    verbose: bool = True,
    output_file: str = None,
):
    print("🧪 Подготовка тестового окружения...")

    if not create_test_database():
        print("❌ Не удалось создать тестовую базу данных")
        return

    env = os.environ.copy()
    env["DEV_ENV_FILE"] = ".env.test"

    cmd = ["pytest", path]

    if verbose:
        cmd.append("-v")

    if marker:
        cmd.extend(["-m", marker])

    cmd.append("--tb=short")  # Короткий traceback

    print(f"🚀 Запуск тестов: {' '.join(cmd)}")

    try:
        if output_file:
            with open(output_file, "w") as f:
                subprocess.run(
                    cmd, env=env, stdout=f, stderr=subprocess.STDOUT, check=True
                )
        else:
            subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError:
        pass


# def create_test_database():
#     print("🛠️ Создаю тестовую базу данных...")

#     db_config = load_env_vars()

#     postgres_container = get_postgres_container_name()
#     print(f"🔍 Используем PostgreSQL: {postgres_container}")

#     user = db_config.get('POSTGRES_USER', 'postgres')
#     password = db_config.get('POSTGRES_PASSWORD', '')
#     host = db_config.get('POSTGRES_HOST', 'localhost')
#     port = db_config.get('POSTGRES_PORT', '5432')
#     db_name = db_config.get('POSTGRES_DB', 'gidrator_db')
#     test_db_name = f"{db_name}_test"

#     try:
#         which_docker = subprocess.run(["which", "docker"], capture_output=True)
#         docker_available = which_docker.returncode == 0

#         if docker_available and postgres_container != "postgres":
#             print(f"🐳 Создаю тестовую БД через Docker контейнер: {postgres_container}")

#             subprocess.run(
#                 ["docker", "exec", "-i", postgres_container, "psql", "-U", user, "-c",
#                 f"DROP DATABASE IF EXISTS {test_db_name};"],
#                 capture_output=True, text=True
#             )

#             # Создаем тестовую БД
#             create_cmd = [
#                 "docker", "exec", "-i", postgres_container, "psql", "-U", user, "-c",
#                 f"CREATE DATABASE {test_db_name};"
#             ]
#             result = subprocess.run(create_cmd, capture_output=True, text=True)

#             if result.returncode == 0:
#                 print(f"✅ Тестовая база данных {test_db_name} создана в контейнере!")
#             else:
#                 print(f"❌ Ошибка создания БД в контейнере: {result.stderr}")
#                 return False
#         else:
#             print(f"🔄 Создаю тестовую БД напрямую через psql...")

#             psql_command = f"psql -U {user} -h {host} -p {port}"
#             if password:
#                 env = os.environ.copy()
#                 env["PGPASSWORD"] = password
#             else:
#                 env = os.environ.copy()

#             drop_cmd = f"{psql_command} -c \"DROP DATABASE IF EXISTS {test_db_name};\""
#             subprocess.run(drop_cmd, shell=True, env=env, capture_output=True)

#             create_cmd = f"{psql_command} -c \"CREATE DATABASE {test_db_name};\""
#             result = subprocess.run(create_cmd, shell=True, env=env, capture_output=True, text=True)

#             if result.returncode == 0:
#                 print(f"✅ Тестовая база данных {test_db_name} создана!")
#             else:
#                 print(f"❌ Ошибка создания тестовой БД: {result.stderr}")
#                 return False

#         test_dsn = f"postgresql://{user}:*******@{host}:{port}/{test_db_name}"
#         print(f"🔄 Тестовая БД доступна: {test_dsn}")

#         return True
#     except Exception as e:
#         print(f"❌ Ошибка при создании тестовой базы данных: {e}")
#         return False


async def create_test_database_async():
    """
    Создает тестовую базу данных используя asyncpg (без psql).
    """
    print("🛠️ Создаю тестовую базу данных...")

    db_config = load_env_vars()

    if not db_config:
        print("❌ Не удалось загрузить конфигурацию БД")
        return False

    user = db_config.get("POSTGRES_USER", "postgres")
    password = db_config.get("POSTGRES_PASSWORD", "")
    host = db_config.get("POSTGRES_HOST", "localhost")
    port = int(db_config.get("POSTGRES_PORT", "5432"))
    db_name = db_config.get("POSTGRES_DB", "gidrator_db")
    test_db_name = f"{db_name}_test"

    print(f"🔍 Подключение к {host}:{port} как {user}")

    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database="postgres",
        )

        await conn.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
        print(f"🗑️ Удалена существующая БД {test_db_name} (если была)")

        await conn.execute(f'CREATE DATABASE "{test_db_name}"')
        print(f"✅ Тестовая база данных {test_db_name} создана!")

        await conn.close()

        test_dsn = f"postgresql://{user}:*******@{host}:{port}/{test_db_name}"
        print(f"🔄 Тестовая БД доступна: {test_dsn}")
        return True

    except Exception as e:
        print(f"❌ Ошибка при создании тестовой базы данных: {e}")
        return False


def create_test_database():
    return asyncio.run(create_test_database_async())


def start_all():
    migrate()
    serve()
