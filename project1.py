import os
import psycopg

filename="/var/log/app.log"

newfile="/root/alerts.txt"

fatalsfile="/root/fatals.txt"

errorsfile="/root/errors.txt"

print("hey")

if os.path.exists(filename):
    with open(filename, 'r') as file:
        entries=file.readlines()

for i in entries:
    if (i[21:25]=="ERRO"):
        length=len(i)
        try: 
            with psycopg.connect(
                    "dbname=log_entries user=postgres password=password host=localhost port=5432"
                ) as connection: 

                with connection.cursor() as my_cursor:

                    my_cursor.execute("INSERT INTO log_entries (timestamp, level, message) VALUES (%s, %s, %s)",
                        (i[0:18], i[21:26], i[28:(length-2)])
                            )
        except Exception as e:
            print("no database found")

    elif (i[21:25]=="FATA"):
        length=len(i)
        try: 
            with psycopg.connect(
                "dbname=log_entries user=postgres password=password host=localhost port=5432"
                ) as connection: 

                with connection.cursor() as my_cursor:

                        my_cursor.execute(
                            "INSERT INTO log_entries (timestamp, level, message) VALUES (%s, %s, %s)",
                            (i[0:18], i[21:26], i[28:(length-2)])
                            )
        except Exception as e:
            print(e)


try: 
    with psycopg.connect(
        "dbname=log_entries user=postgres password=password host=localhost port=5432"
    ) as connection: 

        with connection.cursor() as my_cursor:

            my_cursor.execute("SELECT * FROM log_entries")

            fatals=0
            errors=0
            if os.path.exists(fatalsfile):
                with open(fatalsfile, "r") as file:
                    nums=file.readlines()
                    fatals=int(nums[0])
            if os.path.exists(errorsfile):
                with open(errosfile, "r") as file:
                    nums=file.readlines()
                    errors=int(nums[0])

            records = my_cursor.fetchall() # This returns a list of tuples, that correspond to the rows in the table
            
            inum=0
            ifatals=0
            ierrors=0
            for row in records:
                ifatals=ifatals+1
                ierrors=ierrors+1
                if (row[2]=='FATAL'):
                    if (ifatals>fatals):
                        fatals=fatals+1
                        if os.path.exists(newfile):
                            with open(newfile, 'a') as file: 
                                file.write("alert, fatal log detected \n")
                        else:
                             with open(newfile, 'w') as file: 
                                file.write("alert, fatal log detected \n")
                            
                if (row[2]=='ERROR'):
                    if (ierrors>errors):
                        errors=errors+1
                        if (errors%5==0):
                            if os.path.exists(newfile):
                                with open(newfile, 'a') as file: 
                                    file.write("alert, 5 error logs detected \n") 
                            else:
                                 with open(newfile, 'w') as file: 
                                    file.write("alert, 5 error logs detected \n") 
                with open(fatalsfile, 'w') as file: 
                    file.write(str(fatals))
                with open(errorsfile, 'w') as file: 
                    file.write(str(errors))
except Exception as e:
    print(e)