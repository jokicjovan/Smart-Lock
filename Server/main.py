import httpx
from fastapi import FastAPI, HTTPException
from starlette.responses import Response

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/capture")
async def root():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://192.168.1.177/capture")
            response.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")

    if response.status_code == 200:
        return Response(content=response.content, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")
