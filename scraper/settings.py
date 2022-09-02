import os
from dotenv import load_dotenv
load_dotenv()

postgres = {'environment': os.getenv('ENVIRONMENT'), 'dev_url': os.getenv('DEV_DATABASE_URL'), 'url': os.getenv('DATABASE_URL')
            }

region = {
    'domestic': 'domestic',
    'england': 'england',
    'wales': 'wales',
    'scotland': 'scotland',
    'ni': 'northernireland'
}
