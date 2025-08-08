from twilio.rest import Client
from core.config import settings

client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)