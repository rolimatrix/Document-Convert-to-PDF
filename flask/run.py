from app import create_app
import logging


logging.getLogger('flask_cors').level = logging.DEBUG
app = create_app()


if __name__ == "__main__":

    app.run(debug=True, host='0.0.0.0', port=8080)