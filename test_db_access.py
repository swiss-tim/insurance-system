"""Test if quote data is in the database"""
import sys
sys.path.insert(0, 'src')

from database_queries import get_session
from seed_database import ChatMessage, CustomerUser

session = get_session()

# Check for Maria Weber
user = session.query(CustomerUser).filter(
    CustomerUser.email == 'maria.weber@example.com'
).first()

if not user:
    print("❌ Maria Weber user not found!")
else:
    print(f"✅ Maria Weber found (ID: {user.id})")
    
    # Get ALL her chat messages
    all_messages = session.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.timestamp.desc()).all()
    
    print(f"\n📊 Total ChatMessages: {len(all_messages)}")
    
    if len(all_messages) == 0:
        print("\n⚠️  No messages found - quote was NOT saved to database!")
        print("   Try generating a quote again in the Customer Portal.")
    else:
        print("\n✅ Messages found! Here are the most recent:\n")
        for idx, msg in enumerate(all_messages[:3]):
            print(f"--- Message #{idx+1} ---")
            print(f"Timestamp: {msg.timestamp}")
            print(f"Model: {msg.model_used}")
            print(f"Request: {msg.message[:80]}...")
            print(f"Response: {msg.response[:80]}...")
            print()

session.close()

