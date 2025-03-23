import logging

# Set up logging config
logging.basicConfig(
    filename="simulation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(message: str):
    print(message)
    logging.info(message)
