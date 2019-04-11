import psycopg2
try:
    connection = psycopg2.connect(
								  user = "postgres",
                                  password = "alexdaniel",
                                  dbname = "prototype")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")
    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")

	create_table_query = '''CREATE TABLE articles(
		doc_id serial PRIMARY KEY,
		doc TEXT NOT NULL,
		title TEXT NOT NULL,
		description TEXT NOT NULL,
		content TEXT NOT NULL,
		url TEXT NOT NULL,
		source VARCHAR (150) NOT NULL,
		date DATE
		); '''

    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
