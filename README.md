# Private Art Gallery

Private Art Gallery is a web application built with **FastAPI** that allows users to generate a personalized art gallery based on a search query. The app integrates with the **ArtSearch API** to fetch artworks and the **Wikipedia API** to provide contextual descriptions related to the query.

---

## Features

*  Search artworks by keyword (e.g., artist, style, theme)
*  Display a gallery of images with titles
* Automatically fetch a related summary from Wikipedia
*  Basic analytics:

  * number of results
  * average title length
  * longest and shortest title
*  Input validation and error handling
*  Asynchronous requests for Wikipedia API
*  API key protection using environment variables

---

## 🛠️ Tech Stack

* **Python**
* **FastAPI**
* **ArtSearch API**
* **Wikipedia REST API**
* **httpx (async requests)**
* **dotenv (environment variables)**

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/private-art-gallery.git
cd private-art-gallery
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file and add your API key:

```env
ART_API_KEY=your_api_key_here
```

---

## ▶️ Running the App

```bash
uvicorn main:app --reload
```

Then open in browser:

```
http://127.0.0.1:8000
```

---

## 📡 API Endpoints

### `/`

* HTML form for entering search query

### `/search`

* Parameters:

  * `query` (string, required)
  * `number` (int, 1–10)
* Returns:

  * HTML page with artworks and Wikipedia summary

### `/wiki`

* Fetches Wikipedia summary for given query

---

## ⚠️ Validation & Error Handling

* Only alphanumeric characters and spaces allowed in query
* Minimum query length: 3 characters
* Maximum query length: 100 characters
* API failures handled gracefully (fallback messages shown)

---

##  Example

Search for:

```
Van Gogh
```

Result:

* Gallery of artworks related to Van Gogh
* Short Wikipedia description
* Thumbnail (if available)
* Basic statistics about returned artworks
