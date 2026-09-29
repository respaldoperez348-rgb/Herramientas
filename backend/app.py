from flask import Flask

from backend.config import Config
from backend.controllers.habit_controller import habit_controller


def create_app():
    """
    Crea y configura la aplicación Flask.
    """

    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(
        habit_controller,
        url_prefix="/api"
    )

    @app.route("/")
    def inicio():
        return {
            "app": Config.APP_NAME,
            "version": Config.VERSION,
            "mensaje": "Backend de HabitTracker funcionando correctamente."
        }

    return app


if __name__ == "__main__":
    app = create_app()

    print("=" * 50)
    print("       HABITTRACKER - BACKEND")
    print("=" * 50)
    print("Servidor:")
    print(f"http://{Config.HOST}:{Config.PORT}")
    print("=" * 50)

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
