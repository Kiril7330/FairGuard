import sqlite3

class GuardDB:
    def __init__(self, 
                 db_path="data/guards_system.db"):
        self.conn = sqlite3.connect(db_path)
        self.setup_tables()
        
    def setup_tables(self):
        cursor = self.conn.cursor()
        
        # Creating the table for the names
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS guards (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE NOT NULL
                            )
                       ''')
        
        # Creating the history table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS history (
                            id INTEGER PRIMARY KEY,
                            guard_name TEXT,
                            post_name TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )
                       ''')
        
        self.conn.commit()
        
    def add_guard(self, name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO guards (name) VALUES (?)", (name, ))
            self.conn.commit()
            print(f"Success: Added {name} to the database.")
                
        except sqlite3.IntegrityError:
            print(f"Notice: {name} is already in database!")
            
    def get_next_guard(self, present_guard_names, post_name):
        cursor = self.conn.cursor()
        
        # Adds the correct amount of place holders for the number of guards in the shift
        placeholders = ','.join(['?'] * len(present_guard_names))
        
        # Query to get the last time a guard was on post
        query = f"""
            SELECT g.name, MAX(h.timestamp) as last_done
            FROM guards g
            LEFT JOIN history h ON g.name = h.guard_name AND h.post_name = ?
            WHERE g.name IN ({placeholders})
            GROUP BY g.name
            ORDER BY last_done ASC
            LIMIT 1
        """
        params = [post_name] + present_guard_names
        cursor.execute(query, params)
        
        result = cursor.fetchone()
        
        if result:
            return result[0] # Returns the selected guard
        return None
    
    def record_shift(self, guard_name, post_name):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO history (guard_name, post_name) 
            VALUES (?, ?)
        """, (guard_name, post_name))
        
        self.conn.commit()
        
    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM guards")
        
        return [row[0] for row in cursor.fetchall()]
        
                
 # -- Test --
if __name__ == "__main__":
    db = GuardDB()
                
    db.add_guard("קיריל שמיס")
    db.add_guard("אדם שמאילוב")
                           
            
     # 2. Let's pretend Adam did the scanning post right now
    db.record_shift("אדם שמאילוב", "סריקה")
    print("Recorded a scanning shift for Adam.")
    
    # 3. Now let's ask the database who should do the NEXT scan
    today_team = ["קיריל שמיס", "אדם שמאילוב"]
    next_up = db.get_next_guard(today_team, "סריקה")
    
    print(f"The next person for סריקה is: {next_up}")           
                