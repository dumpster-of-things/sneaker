import sqlite3
import csv
import sys
import re
import os
from urllib.parse import unquote

def query_chrome(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            url,
            title,
            datetime(last_visit_time/1000000 - 11644473600, 'unixepoch') as visit_time_utc
        FROM urls
        ORDER BY last_visit_time DESC;
    """)
    return cursor.fetchall()

def query_safari(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            url,
            title,
            datetime(visit_time + 978307200, 'unixepoch') as visit_time_utc
        FROM history_items
        JOIN history_visits ON history_items.id = history_visits.history_item
        ORDER BY visit_time DESC;
    """)
    return cursor.fetchall()

def query_firefox(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            url,
            title,
            datetime(last_visit_date/1000000, 'unixepoch') as visit_time_utc
        FROM moz_places
        ORDER BY last_visit_date DESC;
    """)
    return cursor.fetchall()

def main():
    database_file = sys.argv[1]
    db_list = database_file.split("/")
    if len(sys.argv) == 2:
        #database_file = sys.argv[1]
        #output_file = database_file+".csv"
        parent_dir = db_list[db_list.index("Users")+1]
    elif len(sys.arg) == 3:
        #database_file = sys.argv[1]
        output_file = sys.argv[2]
        parent_dir = database_file.split("/")[database_file.split("/").index("Users")+1]
    elif len(sys.arg) == 4:
        #database_file = sys.argv[1]
        output_file = sys.argv[2]
        parent_dir = sys.argv[3]
    else:
        print("Usage: script.py <database_file> <output_file>")
        sys.exit(1)
    

    conn = sqlite3.connect(database_file)

    if re.search("^History.*$", database_file.split("/")[-1]):
        if ".db" in database_file:
            data = query_safari(conn)
            try:
                output_file 
            except:
                output_file = "_".join(db_list[db_list.index("Library")+1])+"_"+db_list[-1]+".csv"
                num = 0
                tst = True
                while tst:
                    if os.path.isfile(output_file):
                        num+=1
                        output_file += num
                        continue
                    else:
                        tst=False
        else:
            data = query_chrome(conn)
            try:
                output_file 
            except:
                output_file = "_".join(db_list[db_list.index("Application Support")+1:db_list.index("Default")-1])+"_"+db_list[-1]+".csv"
                num = 0
                tst = True
                while tst:
                    if os.path.isfile(output_file):
                        num+=1
                        output_file += num
                        continue
                    else:
                        tst=False
    elif re.search("^places.*\.sqlite$", database_file.split("/")[-1]):
        data = query_firefox(conn)
        try:
            output_file 
        except:
            output_file = "_".join(db_list[db_list.index("Application Support")+1:db_list.index("Profiles")-1])+"_"+db_list[-1]+".csv"
            num = 0
            tst = True
            while tst:
                if os.path.isfile(output_file):
                    num+=1
                    output_file += num
                    continue
                else:
                    tst=False
    else:
        print("Unknown database file!")
        sys.exit(1)

    conn.close()

    #data = [(unquote(row[0]), row[1], row[2], parent_dir) for row in data]
    
    data = [(row[0], row[1], row[2], parent_dir, " ".join(" ".join(unquote(row[0]).split("&")).split("?")).split(" ")) for row in data]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['URL', 'Title', 'Visit Time UTC', 'Parent Directory', 'Decoded URL Params'])
        writer.writerows(data)

if __name__ == "__main__":
    main()
