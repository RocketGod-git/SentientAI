import os
import logging
import logging.handlers

# The CustomFormatter class is responsible for formatting log messages according to their severity level.
# It provides color-coded output for different levels.
class CustomFormatter(logging.Formatter):

    # Here we define the color codes for the different logging levels. 
    # We use escape sequences to represent colors.
    LEVEL_COLORS = [
        (logging.DEBUG, '\x1b[40;1m'),  # DEBUG level logs will appear in bright black.
        (logging.INFO, '\x1b[34;1m'),   # INFO level logs will appear in bright blue.
        (logging.WARNING, '\x1b[33;1m'), # WARNING level logs will appear in bright yellow.
        (logging.ERROR, '\x1b[31m'),    # ERROR level logs will appear in red.
        (logging.CRITICAL, '\x1b[41m'), # CRITICAL level logs will appear with red background.
    ]

    # We define a formatter for each level with its own color.
    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {color}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m -> %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        for level, color in LEVEL_COLORS
    }

    def format(self, record):
        # For a given log record, find its formatter based on its level.
        formatter = self.FORMATS.get(record.levelno)
        # If no formatter found for the level, default to DEBUG formatter.
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]
 
        # If the record has exception info, format it and colorize in red.
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        # Generate the final formatted string.
        output = formatter.format(record)

        # Clean up the exception text to prevent any interference with subsequent log records.
        record.exc_text = None
        return output


# Function to set up a logger for a given module.
def setup_logger(module_name:str) -> logging.Logger:
    # Extract the library name from the module name.
    library, _, _ = module_name.partition('.py')
    # Create a logger with the library name and set its level to INFO.
    logger = logging.getLogger(library)
    logger.setLevel(logging.INFO)
    
    # Create a console handler and set its level to INFO.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CustomFormatter())
    
    # Determine the grandparent directory of the current script file.
    grandparent_dir = os.path.abspath(__file__ + "/../../")
    log_name='chatgpt_discord_bot.log'
    # Define the log file path by joining the grandparent directory and log name.
    log_path = os.path.join(grandparent_dir, log_name)
    
    # Create a file log handler that will write logs to a local file and rotate them when it reaches 32 MiB size.
    # It will keep only the 2 most recent log files.
    log_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=2,  # Keep only 2 most recent logs
    )
    
    # Apply our custom log formatter to the log file handler.
    log_handler.setFormatter(CustomFormatter())
    
    # Add both console and file handlers to the logger.
    logger.addHandler(log_handler)
    logger.addHandler(console_handler)

    # Return the configured logger.
    return logger