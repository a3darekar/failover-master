from logger_config import logger, pingLogger
from server import socketio, app

if __name__ == "__main__":
	gunicorn_logger = logging.getLogger('gunicorn.error')
	logger.handlers = gunicorn_logger.handlers
	logger.info("recovery server active")
	socketio.run(app)