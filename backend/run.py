import sys
import os
from loader import wait_for_db, create_tables, load_pickle_data
import uvicorn

if __name__ == "__main__":
    # stdout/stderr unbuffered
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
    
    print("Data loader starting...")
    sys.stdout.flush()
    
    if not wait_for_db():
        print("wait_for_db failed")
        sys.stdout.flush()
        sys.exit(1)
    
    if not create_tables():
        print("create_tables failed")
        sys.stdout.flush()
        sys.exit(1)
    
    if not load_pickle_data():
        print("load_pickle_data failed")
        sys.stdout.flush()
        sys.exit(1)
    
    print("Data loading completed. Starting uvicorn...")
    sys.stdout.flush()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
