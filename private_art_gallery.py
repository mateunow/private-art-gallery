from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import artsearch
import httpx
import re
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()

configuration = artsearch.Configuration(
    host="https://api.artsearch.io"
)
api_key = os.getenv("ART_API_KEY")
configuration.api_key['apiKey'] = api_key
configuration.api_key['headerApiKey'] = api_key

if not api_key:
    raise Exception("Brak API KEY w zmiennych środowiskowych")

@app.get("/", response_class=HTMLResponse)
async def form():
    return """
    <html>
        <body>
            <h2>Wyszukiwarka sztuki</h2>
            <form action="/search">
            <label for="query">Wpisz wyszukiwane hasło:</label>
                <input type="text" name="query" placeholder="np. Van Gogh" required>
                <label for="number">Liczba wyników:</label>
                <input type='number' name='number' placeholder='Liczba wyników' min='1' max='10' value='10'>
             
                <button type="submit">Szukaj</button>
            </form>
        </body>
    </html>
    """
@app.get("/wiki")
async def wiki_api(query: str):
    return await get_wikipedia_data(query)

async def get_wikipedia_data(query: str):
    query = query.replace(" ", "_")
    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "ArtSearchApp/1.0 (mateusz@example.com)"
            }
            response = await client.get(wiki_url, headers=headers)

        if response.status_code != 200:
            return {"description": "Brak danych", "thumbnail": None}

        data = response.json()

        return {
            "description": data.get("extract") or data.get("description"),
            "thumbnail": data.get("thumbnail", {}).get("source")
        }
    except Exception as e:
        print("WIKI ERROR:", e)
        description = "Nie można pobrać danych z Wikipedii (brak internetu/ błąd API)"
        return {"description": description, "thumbnail": None}

@app.get("/search", response_class=HTMLResponse)
async def search(query: str = Query(...), number: int = Query(10, ge=1, le=10)):
    
    if not re.match(r"^[a-zA-Z0-9\s]+$", query):
        raise HTTPException(status_code=400, detail="Invalid characters")
    if not query or len(query) <= 2:
        raise HTTPException(status_code=400, detail="Query longer than 2 characters is required")
    if len(query) > 100:
        raise HTTPException(status_code=400, detail="Query must be 100 characters or less")

    with artsearch.ApiClient(configuration) as api_client:
        api_instance = artsearch.ArtApi(api_client)

        try:
            artworks = api_instance.search_artworks(query=query, number=number)
        except Exception as e:
            return f"<h3>Błąd pobierania danych z ArtSearch: {e}</h3>"
    
    wiki_data = await get_wikipedia_data(query)
    description = wiki_data["description"]
    thumbnail = wiki_data["thumbnail"]

    titles = []
    images = []
    if artworks and hasattr(artworks, "artworks"):
        for art in artworks.artworks:
            titles.append(getattr(art, "title", "Brak tytułu"))
            images.append(getattr(art, "image", None))

    count = len(titles)

    html = f"<h2>Wyniki dla: {query}</h2>"
    html += f"<p><b>Liczba dzieł:</b> {count}</p>"

    for i in range(count):
        html += f"<h3>{titles[i]}</h3>"
        if i < len(images):
            html += f"<img src='{images[i]}' width='650' alt='{titles[i]}' style='display: block; margin: 0 auto;'><br>"
            html += f"<p><b>Title:</b> {titles[i]} </p>"
            html += f"<p><b>Image URL:</b> <a href='{images[i]}' target='_blank'>{images[i]}</a></p>"
    if len(titles) == 0:
        html += "<p>Brak wyników z ArtSearch</p>"

    lengths = [len(title) for title in titles]

    avg_length = sum(lengths) / len(lengths) if lengths else 0
    longest_title = max(titles, key=len) if titles else "Brak"
    shortest_title = min(titles, key=len) if titles else "Brak"

    html += f"<p><b>Średnia długość tytułu:</b> {avg_length:.2f}</p>"
    html += f"<p><b>Najdłuższy tytuł:</b> {longest_title}</p>"
    html += f"<p><b>Najkrótszy tytuł:</b> {shortest_title}</p>"
    
    html += f"<p><b>Opis z Wikipedii do danego wyszukiwania:</b> {description}</p>"
    if thumbnail:
        html += f"<img src='{thumbnail}' width='500' alt='Thumbnail' align='middle'><br>"
    html += f"<p><b>Źródło danych z Wikipedii:</b> <a href='https://en.wikipedia.org/wiki/{query}' target='_blank'>https://en.wikipedia.org/wiki/{query}</a></p>"
    
    return html