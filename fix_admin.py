import sqlite3
conn = sqlite3.connect('backend/database.db')
c = conn.cursor()
c.execute("UPDATE users SET role='admin' WHERE email='[EMAIL_ADDRESS]'")
conn.commit()
print("Updated admin role")
