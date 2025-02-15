import subprocess
import os

# Apply ACLs to /data directory at runtime (only if not already applied)
def apply_acls():
    if not os.path.exists('/data/.immutable_flag'):
        # Set ACLs to allow read/write but prevent deletion
        subprocess.run(['setfacl', '-d', '-m', 'u::rw', '/data'], check=True)
        subprocess.run(['setfacl', '-d', '-m', 'g::rw', '/data'], check=True)
        subprocess.run(['setfacl', '-d', '-m', 'o::r', '/data'], check=True)
        
        # Mark that ACLs were applied
        with open('/data/.immutable_flag', 'w') as f:
            f.write('ACLs applied')

# Apply ACLs
apply_acls()

# Here, you can start your FastAPI or any other process
from uvicorn import run

# Get port from environment variables (default to 8090 if not set)
port = int(os.getenv("PORT", 8000))
run(app="main:app", host="0.0.0.0", port=port)
