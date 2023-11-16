from bot_controller.handlers import Bot
from db.db_app import setup_table

if __name__ == '__main__':
    setup_table()
    Bot().bot_runner()
