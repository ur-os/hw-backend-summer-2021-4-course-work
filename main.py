import os

from app.web.app import setup_app
from aiohttp.web import run_app

# FILE_PATH = '/home/urick0s/PycharmProjects/hw-backend-summer-2021-3-db_gino/'

if __name__ == "__main__":
    run_app(setup_app(config_path=os.path.join(os.path.dirname(__file__), 'config.yml')))
