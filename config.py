import logging

def configure_logging():
    success_logger = logging.getLogger('success_logger')
    error_logger = logging.getLogger('error_logger')
    
    success_handler = logging.FileHandler('success.log')
    error_handler = logging.FileHandler('error.log')
    
    success_handler.setLevel(logging.INFO)
    error_handler.setLevel(logging.ERROR)
    
    success_formatter = logging.Formatter('%(asctime)s - %(message)s')
    error_formatter = logging.Formatter('%(asctime)s - %(message)s')
    
    success_handler.setFormatter(success_formatter)
    error_handler.setFormatter(error_formatter)
    
    success_logger.addHandler(success_handler)
    error_logger.addHandler(error_handler)
    
    return success_logger, error_logger
