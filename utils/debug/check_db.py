#!/usr/bin/env python3
from services import get_neo4j_service

def check_user_data(user_id):
    neo4j = get_neo4j_service()
    
    # Get User node
    user_query = f'MATCH (u:User {{userId: "{user_id}"}}) RETURN u'
    user_results = neo4j.run_query(user_query)
    
    print("=== USER DATA ===")
    if user_results:
        for r in user_results:
            print(r['u'])
    else:
        print(f"No User node found with ID: {user_id}")
    
    # Get EmailLookup node
    lookup_query = f'MATCH (e:EmailLookup {{userId: "{user_id}"}}) RETURN e'
    lookup_results = neo4j.run_query(lookup_query)
    
    print("\n=== EMAIL LOOKUP ===")
    if lookup_results:
        for r in lookup_results:
            print(r['e'])
    else:
        print(f"No EmailLookup node found for ID: {user_id}")
    
if __name__ == "__main__":
    user_id = "U_5032c061-81f9-44cb-91ce-0ee326417cfc"
    check_user_data(user_id) 