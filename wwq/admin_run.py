
from run import app
from config.config import logger


if __name__ == '__main__':
    logger.debug('run 0.0.0.0:8815')
    app.run(
        host='0.0.0.0',
        port=8815
        ##threaded=True
    )