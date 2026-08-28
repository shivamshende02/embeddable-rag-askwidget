from app.core.config import get_settings

settings = get_settings()
print(f"Business: {settings.BUSINESS_NAME}")
print(f"Allowed Origin: {settings.ALLOWED_ORIGIN}")
print(f"Greeting: {settings.GREETING_MESSAGE}")