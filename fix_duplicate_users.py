#!/usr/bin/env python3
"""
Fix duplicate users script
This script cleans up duplicate User and EmailLookup records in the Neo4j database
"""

import logging
from services import get_neo4j_service

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def fix_duplicate_users():
    """Clean up duplicate users and EmailLookup entries"""
    try:
        neo4j_service = get_neo4j_service()
        
        print("🔍 Checking for duplicate EmailLookup entries...")
        
        # Find duplicate EmailLookup entries
        with neo4j_service.driver.session() as session:
            result = session.run("""
                MATCH (e:EmailLookup)
                WITH e.email as email, collect(e) as lookups
                WHERE size(lookups) > 1
                RETURN email, size(lookups) as count, lookups
            """)
            
            duplicates = list(result)
            if duplicates:
                print(f"❌ Found {len(duplicates)} emails with duplicate EmailLookup entries:")
                for record in duplicates:
                    email = record["email"]
                    count = record["count"]
                    print(f"   - {email}: {count} entries")
                
                # Fix duplicates by keeping only the first entry for each email
                for record in duplicates:
                    email = record["email"]
                    lookups = record["lookups"]
                    
                    # Keep the first lookup entry, delete the rest
                    keep_lookup = lookups[0]
                    delete_lookups = lookups[1:]
                    
                    print(f"🔧 Fixing {email}: keeping {keep_lookup['userId']}, deleting {len(delete_lookups)} duplicates")
                    
                    for lookup in delete_lookups:
                        session.run("""
                            MATCH (e:EmailLookup)
                            WHERE id(e) = $lookup_id
                            DELETE e
                        """, lookup_id=lookup.id)
                        
                        # Also delete the associated User node if it exists
                        user_id = lookup['userId']
                        session.run("""
                            MATCH (u:User {userId: $user_id})
                            DETACH DELETE u
                        """, user_id=user_id)
                        
                        print(f"   ✅ Deleted duplicate user {user_id}")
                
                print("✅ Fixed all duplicate EmailLookup entries")
            else:
                print("✅ No duplicate EmailLookup entries found")
        
        # Check for orphaned User nodes (without corresponding EmailLookup)
        print("\n🔍 Checking for orphaned User nodes...")
        with neo4j_service.driver.session() as session:
            result = session.run("""
                MATCH (u:User)
                WHERE NOT EXISTS {
                    MATCH (e:EmailLookup {userId: u.userId})
                }
                RETURN u.userId as user_id, u.email as hashed_email
            """)
            
            orphaned_users = list(result)
            if orphaned_users:
                print(f"❌ Found {len(orphaned_users)} orphaned User nodes:")
                for record in orphaned_users:
                    user_id = record["user_id"]
                    print(f"   - {user_id}")
                    
                    # Delete orphaned user nodes
                    session.run("""
                        MATCH (u:User {userId: $user_id})
                        DETACH DELETE u
                    """, user_id=user_id)
                    print(f"   ✅ Deleted orphaned user {user_id}")
                
                print("✅ Cleaned up all orphaned User nodes")
            else:
                print("✅ No orphaned User nodes found")
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        with neo4j_service.driver.session() as session:
            # Check EmailLookup entries
            result = session.run("MATCH (e:EmailLookup) RETURN count(e) as total_lookups")
            total_lookups = result.single()["total_lookups"]
            
            # Check User nodes
            result = session.run("MATCH (u:User) RETURN count(u) as total_users")
            total_users = result.single()["total_users"]
            
            # Check for duplicates again
            result = session.run("""
                MATCH (e:EmailLookup)
                WITH e.email as email, count(e) as count
                WHERE count > 1
                RETURN count(*) as duplicate_emails
            """)
            duplicate_emails = result.single()["duplicate_emails"]
            
            print(f"📊 Final state:")
            print(f"   - Total EmailLookup entries: {total_lookups}")
            print(f"   - Total User nodes: {total_users}")
            print(f"   - Duplicate emails: {duplicate_emails}")
            
            if duplicate_emails == 0:
                print("🎉 SUCCESS: All duplicates have been fixed!")
            else:
                print("⚠️  WARNING: Some duplicates still exist")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing duplicate users: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧹 Starting duplicate user cleanup...")
    success = fix_duplicate_users()
    if success:
        print("\n✅ Duplicate user cleanup completed successfully!")
    else:
        print("\n❌ Duplicate user cleanup failed!") 