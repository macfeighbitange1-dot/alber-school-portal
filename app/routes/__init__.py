from flask import Blueprint

# 1. Import the actual Blueprint objects from the logic files
from .portal import portal
from .api import api
# We define payments_bp in its own file now to be safe, so we import it here:
from .payments import payments_bp 

# 2. Define placeholders for ones we haven't built separate files for yet
auth = Blueprint('auth', __name__)

# Note: We removed payments_bp = Blueprint(...) from here because 
# it is now defined inside app/routes/payments.py