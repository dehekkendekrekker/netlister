from loguru import logger

def abort(message):
    logger.error(message)
    quit()