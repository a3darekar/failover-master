from server import app, socketio, logger, pingLogger


if __name__ == "__main__":
	logger = logging.getLogger("operations")
	pingLogger = logging.getLogger("ping")

	logger.info("recovery server active")
	socketio.run(app)