from MySQLConnector import MySQLConnector


def search_users_by_keyword(keyword):
    connector = MySQLConnector()
    connector.get_server_connection()
    
    query = """
        SELECT id, name, description, followers_count
        FROM twitter_users
        WHERE description LIKE %s OR name LIKE %s
        ORDER BY followers_count DESC
        LIMIT 10;
    """
    # Use % to denote wildcard matches before and after the keyword
    values = (f"%{keyword}%", f"%{keyword}%")
    
    results = connector.execute_query(query, values)
    
    # for user in results:
    #     print(user)  # Print each user found by the query

    return results
    
    connector.close_server_connection()

# Example usage
if __name__ == "__main__":
    keyword = input("Enter a keyword to search in users: ")
    results = search_users_by_keyword(keyword)
    print(results)
