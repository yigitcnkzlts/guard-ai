from unittest.mock import MagicMock, PropertyMock, patch

from app.database.bootstrap import bootstrap_database


def test_bootstrap_is_disabled_for_regular_databases() -> None:
    with (
        patch(
            "app.database.bootstrap.settings.__class__.should_bootstrap_database",
            new_callable=PropertyMock,
            return_value=False,
        ),
        patch("app.database.bootstrap.Base.metadata.create_all") as create_all,
    ):
        bootstrap_database()

    create_all.assert_not_called()


def test_bootstrap_creates_schema_and_seeds_demo_data() -> None:
    session = MagicMock()
    session_context = MagicMock()
    session_context.__enter__.return_value = session

    with (
        patch(
            "app.database.bootstrap.settings.__class__.should_bootstrap_database",
            new_callable=PropertyMock,
            return_value=True,
        ),
        patch("app.database.bootstrap.Base.metadata.create_all") as create_all,
        patch("app.database.bootstrap.SessionLocal", return_value=session_context),
        patch("app.database.bootstrap.seed_customer_support_agent") as seed_support,
        patch("app.database.bootstrap.seed_finance_agent") as seed_finance,
        patch("app.database.bootstrap.seed_developer_agent") as seed_developer,
    ):
        bootstrap_database()

    create_all.assert_called_once()
    seed_support.assert_called_once_with(session)
    seed_finance.assert_called_once_with(session)
    seed_developer.assert_called_once_with(session)
