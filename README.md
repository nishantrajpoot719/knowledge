# Knowledge API

A Flask-based API for the Knowledge Agent that handles general inquiries and FAQs.

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd knowledge_api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your environment variables:
   ```
   FLASK_DEBUG=true
   PORT=5000
   # Add other environment variables as needed
   ```

## Running Locally

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### GET /
- **Description**: Health check endpoint
- **Response**: `"Knowledge API is running!"`

### POST /query
- **Description**: Process a user query
- **Request Body**:
  ```json
  {
    "query": "Your question here"
  }
  ```
- **Response**:
  ```json
  {
    "query": "Your question here",
    "response": "The agent's response"
  }
  ```

## Deployment to Render

1. Push your code to a GitHub repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the following settings:
   - **Name**: knowledge-api (or your preferred name)
   - **Region**: Choose the closest to your users
   - **Branch**: main (or your preferred branch)
   - **Runtime**: Python 3.9+
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add any necessary environment variables
6. Deploy!

## Environment Variables

- `PORT`: The port the app will run on (default: 5000)
- `FLASK_DEBUG`: Set to 'true' for development mode
- Add any other required API keys and secrets
