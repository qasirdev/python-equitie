import os
import sys

# Ensure backend module can be imported in Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from backend.main import app

# Vercel serverless entrypoint
handler = Mangum(app)
