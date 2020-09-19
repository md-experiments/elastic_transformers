import logging
import datetime
import os

logs_folder='logs'
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)

# Create a custom logger
logger = logging.getLogger(__name__)

# Setting global logging level
logger.setLevel(logging.WARNING)

date=str(datetime.date.today()).replace('-','')
# Initialize handlers
file_hndl = logging.FileHandler(f'{logs_folder}/q_logs_{date}.log')
cli_hndl = logging.StreamHandler()
# Set logging level
file_hndl.setLevel(level=logging.DEBUG)
cli_hndl.setLevel(level=logging.DEBUG)
# Add formatters to handlers
logger_text_format = logging.Formatter('%(asctime)s --- %(name)s --- %(levelname)s --- %(funcName)s:%(lineno)d --- %(message)s')
file_hndl.setFormatter(logger_text_format)
cli_hndl.setFormatter(logger_text_format)

# Add handlers to the logger
logger.addHandler(file_hndl)
logger.addHandler(cli_hndl)

