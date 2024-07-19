from app.config.config import settings
from app.auth.auth import Auth0

auth0_domain = settings.AUTH0_DOMAIN
auth0_api_audience = settings.AUTH0_API_AUDIENCE
auth = Auth0(domain=auth0_domain, api_audience=auth0_api_audience, scopes={})
