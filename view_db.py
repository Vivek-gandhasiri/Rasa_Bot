import sqlite3

def view_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    print("Users Table:")
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    for user in users:
        print(user)

    print("\nMatches Table:")
    c.execute("SELECT * FROM matches")
    matches = c.fetchall()
    for match in matches:
        print(match)

    conn.close()

if __name__ == '__main__':
    view_data()
