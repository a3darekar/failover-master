import logging

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

logger = logging.getLogger('operations')
fileHandler = logging.FileHandler('operations.log')
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

pingLogger = logging.getLogger('ping')
pingFileHandler = logging.FileHandler('ping.log')
pingFileHandler.setFormatter(formatter)
pingLogger.addHandler(pingFileHandler)
pingLogger.setLevel(logging.INFO)

ch = logging.StreamHandler() 			# Console Log Handler
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
pingLogger.addHandler(ch)