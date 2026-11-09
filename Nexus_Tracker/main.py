from database import crear_tablas
from scheduler import iniciar_scheduler


def main():

    print(
        "Iniciando Nexus Task Tracker..."
    )

    crear_tablas()

    iniciar_scheduler()


if __name__ == "__main__":

    main()
