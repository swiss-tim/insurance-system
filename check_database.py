"""Quick diagnostic script to check database state"""
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
    print("❌ ERROR: Maria Weber user not found in database!")
    print("   Run: python src/seed_database.py")
else:
    print(f"✅ Maria Weber found (ID: {user.id})")
    
    # Count her chat messages
    total_messages = session.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).count()
    
    print(f"✅ Total ChatMessages for Maria: {total_messages}")
    
    if total_messages == 0:
        print("\n⚠️  No chat messages found!")
        print("   To fix:")
        print("   1. Open Customer Portal (http://localhost:8503)")
        print("   2. Go to 'Special Offers' tab")
        print("   3. Click 'Get Free Quote' on any product")
        print("   4. Wait for chat to complete")
        print("   5. Refresh Guidewire Backend to see the quote")
    else:
        print(f"\n✅ Database has {total_messages} messages")
        print("   Guidewire Backend should show them!")
        
        # Show most recent
        recent = session.query(ChatMessage).filter(
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.timestamp.desc()).first()
        
        if recent:
            print(f"\n📋 Most Recent Message:")
            print(f"   Timestamp: {recent.timestamp}")
            print(f"   Request: {recent.message[:50]}...")
            print(f"   Response: {recent.response[:50]}...")

session.close()

