from fastapi import FastAPI, HTTPException, Depends
import httpx
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# FatSecret API Credentials
CLIENT_ID = os.getenv("FATSECRET_CLIENT_ID")
CLIENT_SECRET = os.getenv("FATSECRET_CLIENT_SECRET")
TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
SEARCH_URL = "https://platform.fatsecret.com/rest/server.api"

app = FastAPI()

class FoodSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10

# Function to get OAuth 2.0 token
async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(CLIENT_ID, CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to obtain access token")
        return response.json()["access_token"]

@app.post("/search_foods/")
async def search_foods(request: FoodSearchRequest, access_token: str = Depends(get_access_token)):
    params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": request.query,
        "max_results": request.max_results
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(SEARCH_URL, params=params, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching food data")

        return response.json()
