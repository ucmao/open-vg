"""Quick script to add credits to a user account."""
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal
from app.models.user import User
from app.models.credit_record import CreditType
from app.services.credit_service import add_credits as credit_service_add_credits

def add_credits(email: str, amount: int = 1000):
    """Add credits to user account."""
    db = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return
        
        new_balance = credit_service_add_credits(
            db,
            user.id,
            amount,
            CreditType.RECHARGE,
            "Manual credit top-up (dev mode)",
        )
        db.commit()
        
        print(f"✅ Successfully added {amount} credits to {email}")
        print(f"   New balance: {new_balance} credits")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        try:
            amount = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        except ValueError:
            print("❌ Invalid amount. Using default 1000.")
            amount = 1000
    else:
        email = input("Enter user email: ")
        try:
            amount_input = input("Enter credits amount (default 1000): ")
            amount = int(amount_input) if amount_input.strip() else 1000
        except ValueError:
            print("❌ Invalid input. Using default 1000.")
            amount = 1000
    
    add_credits(email, amount)
