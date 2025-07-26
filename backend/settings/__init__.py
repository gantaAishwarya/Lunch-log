import os
env = os.environ.get("ENVIRONMENT", "dev")

if env == "prod":
    from .prod import *
else:
    from .dev import *
