from Flask.routes import app
import logging
from logging.handlers import RotatingFileHandler
import os

logfile = os.path.abspath(os.path.relpath("Logs"))
logger = logging.getLogger("Flask")
logger.setLevel(logging.DEBUG)
fh = RotatingFileHandler(os.path.join(logfile, 'precise.log'), maxBytes=50000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

if __name__ == "__main__":
  app.run(debug=True)
