# Memoire

## Run

Install pip package

```bash
uv sync
```

SQL Migration (PG need to be able to install pgvector)

```bash
uv run manage.py migrate
```

Launch Django server

```bash
uv run manage.py runserver
```

## Celery Tasks

The project uses Celery with Redis for background tasks. To run the task system:

1. Make sure Redis is running on localhost:6379
2. Start the Celery worker:

```bash
uv run celery -A memoire worker -l INFO
```

3. Start the Celery beat scheduler (for periodic tasks):

```bash
uv run celery -A memoire beat -l INFO
```

The system includes a daily task that:

- Checks for users with more than 10 memories
- Creates a summary of unsurmmarized memories using an LLM
- Marks the original memories as summarized
- Stores the summary as a new memory with metadata

## TODO

- [ ] Need to check if memory contredict themselves
- [x] Compact old memory and make a summary
