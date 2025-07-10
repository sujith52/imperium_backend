from fastapi import Header, HTTPException, Depends

API_KEY = "mysecretkey123"  # replace with an environment variable in production

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
