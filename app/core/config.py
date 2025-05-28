class JWT:
    SECRET_KEY = "supersecret_key_change_in_production"  # In production, store in env var
    ALGORITHM = "HS256"
    EXPIRATION_MINUTES = 30
    ISSUER = "https://api.globomantics.com"  # URI that identifies token issuer