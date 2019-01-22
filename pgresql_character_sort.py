# keylog.py - prompt user to insert text, either manually or from clipboard
#		  	  then categorize all characters and print out the amount of each
#			  character used in the input, then write the results to a pgsql table


import os, sys, pyperclip, time
import psycopg2 as p2

# set up connection with psql db
con = p2.connect("dbname='sample_db' user='postgres' host='' password=''")
cur = con.cursor()

#collect time for run length
start_time = time.time()


### LOOK FOR TABLE EXISTS CONDITION ###

# get table names to look for 'keylog' table
cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
tables_raw = cur.fetchall()

#reformat the resulting tuples in tables_raw into simple strings
tables = []
for i in range(len(tables_raw)):
	tables.append(tables_raw[i][0])

#see if 'keylog' table exists, delete data if it does
if 'keylog' not in tables:
	cur.execute("CREATE TABLE keylog (rank varchar(10), key varchar(1), used int);") #varchar(10));")
	con.commit()
else:
	cur.execute("DELETE FROM keylog;")
	con.commit()



### CREATE DATA LIST AND WRITE TO TABLE ###

# gather text from clipboard
clipboard = pyperclip.paste()

# create dict of characters and their usage
chars = {}
for ch in clipboard:
	if ch not in chars:
		chars[ch.lower()] = 1
	else:
		chars[ch] += 1

# write to table
i = 1
for key, value in sorted(chars.items(), key=lambda x: x[1], reverse=True):
	cur.execute(f"INSERT INTO keylog (rank, key, used) VALUES ('{i}', '{key}', '{int(value)}');")
	con.commit()
	i+=1

# get total time of process
end_time = time.time()
total_time = end_time - start_time
print('Process Completed in '+ str(total_time)[:5]+'s')
