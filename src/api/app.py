from flask import Flask, render_template
from flask_cors import CORS
from src.api.routes import api


def create_app():
    app = Flask(
        __name__,
        template_folder="../../dashboard/templates",
        static_folder="../../dashboard/static",
    )
    CORS(app)
    app.register_blueprint(api, url_prefix="/api")

    @app.route("/")
    def dashboard():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
