# RAG Web App Project

This project focuses on developing a web application that enables private corporations to retrieve documentation. The application allows users to obtain information about variables or techniques used in their technologies through question answering, utilizing Large Language Models (LLMs).

## Getting Started

Follow these steps to set up the project locally:

1. **Clone the repository** (You can use HTTPS too):
   ```bash
   git clone git@github.com:TurkuNLP/RAG-web-app.git
2. **Create a virtual environment** :
   ```bash
   python3 -m venv env
*Note: Replace env with your preferred environment name.*

3. **Activate the virtual environment** :   
   ```bash
   source env/bin/activate

4. **Install dependencies** :   
   ```bash
   pip install -r /path/to/requirements.txt

## Run an App (Single Entry Point)

Use `run.py` to select which Flask app to run with `APP_NAME`. Optional `PORT`, `HOST`, and `DEBUG` environment variables control runtime.

Supported apps (`APP_NAME`):
- `local`
- `seus`
- `arch-ru`
- `arch-en`
- `news`
- `law`

Examples:
```bash
APP_NAME=local PORT=5000 python run.py
APP_NAME=law PORT=8080 python run.py
APP_NAME=arch-en python run.py
```

## Docker

Build the image:
```bash
docker build -t rag-web-app .
```

Run a selected app:
```bash
docker run --rm -p 8000:8000 \
  -e APP_NAME=local \
  -e PORT=8000 \
  rag-web-app
```

Using Docker Compose:
```bash
docker compose up --build
```

Change the app by editing `APP_NAME` in `docker-compose.yml` or passing `-e APP_NAME=law` to `docker run`.

## Conda Environment (Optional)

If you use Conda, create an environment and install Python dependencies with pip:
```bash
conda create -n rag-web-app python=3.11
conda activate rag-web-app
pip install -r requirements.txt
```

## Configuration (config.json)

`config.json` stores configuration settings for different environments or use cases. Each configuration specifies:

- `data_path`: Path to the data folder.
- `chroma_root_path`: Path where the Chroma database will be stored.
- `embedding_model`: Name of the model used for embeddings.
- `llm_model`: Name of the language model to be used.

## Environment Variables

API keys are loaded from a `.env` file via `python_script/parameters.py`. Common keys:

- `OPENAI_API_KEY`: required when using OpenAI models.
- `HF_API_TOKEN`: required when using Hugging Face hosted models.
- `VOYAGE_API_KEY`: required when using VoyageAI models (if enabled).

Runtime settings:

- `APP_NAME`: which app to run (see Supported apps above).
- `HOST`: bind address (default `0.0.0.0`).
- `PORT`: port to listen on (defaults to the app’s configured port).
- `DEBUG`: set to `true`/`1` to enable Flask debug (local dev only).

## Database Scripts (python_script/)

Four files in `python_script/` are related to database setup and management:

- `parameters.py`: loads parameters from `config.json`.
- `get_embedding_function.py`: loads the embedding model.
- `populate_database.py`: create, reset, or clear the database.

### populate_database.py

The `main()` function is the CLI entry point for database management.

Arguments:
- `--config` (str): configuration name in `config.json`.
- `--reset`: clear the database subfolder for the config, then repopulate.
- `--clear`: clear the database (optionally scoped to the config).

Functionality:
- **Populate**: `--config` only loads documents, splits them, and adds them to Chroma.
- **Reset**: `--config --reset` clears the config’s subfolder, then repopulates.
- **Clear**: `--clear` removes data; if `--config` is provided, it targets the config’s subfolder (based on `EMBEDDING_MODEL`).

Example usage:
```bash
python populate_database.py --config CONFIG_NAME
python populate_database.py --config CONFIG_NAME --reset
python populate_database.py --config CONFIG_NAME --clear
```
