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

## TODO

- [ ] Need to check if memory contredict themselves
- [ ] Compact very old memory and a summary
