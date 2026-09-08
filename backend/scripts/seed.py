from app.database.session import SessionLocal
from app.services.bootstrap import (
    seed_customer_support_agent,
    seed_developer_agent,
    seed_finance_agent,
)


def main() -> None:
    db = SessionLocal()
    try:
        print("Seeding agents and policies...")
        
        csa = seed_customer_support_agent(db)
        print(f"✓ Seeded '{csa.name}' with {len(csa.policies)} policies")
        
        fa = seed_finance_agent(db)
        print(f"✓ Seeded '{fa.name}' with {len(fa.policies)} policies")
        
        da = seed_developer_agent(db)
        print(f"✓ Seeded '{da.name}' with {len(da.policies)} policies")
        
        print("Seed complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
