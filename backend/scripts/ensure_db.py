"""Create the GUARD PostgreSQL database if it does not already exist."""

from sqlalchemy.engine.url import make_url

from app.core.config import settings


def ensure_database() -> None:
    url = make_url(settings.DATABASE_URL)
    if not url.drivername.startswith("postgresql"):
        return

    db_name = url.database
    if not db_name:
        return

    import psycopg
    from psycopg import sql

    with psycopg.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        dbname="postgres",
        autocommit=True,
    ) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,),
        ).fetchone()
        if exists:
            print(f"Database '{db_name}' already exists.")
            return
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Created database '{db_name}'.")


def main() -> None:
    ensure_database()


if __name__ == "__main__":
    main()
