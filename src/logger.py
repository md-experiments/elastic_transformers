import logging
import datetime
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Create handlers
dt=str(datetime.date.today()).replace('-','')
f_handler = logging.FileHandler(f'logs/q_logs_{dt}.log')
f_handler.setLevel(level=logging.DEBUG)
c_handler = logging.StreamHandler()
c_handler.setLevel(level=logging.DEBUG)
# Create formatters and add it to handlers
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
f_handler.setFormatter(f_format)
c_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(f_handler)
logger.addHandler(c_handler)

