from twilio.rest import Client
from .config import settings

client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)