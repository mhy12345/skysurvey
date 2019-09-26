import mysql.connector
from mysql.connector import Error
from mysql.connector import cursor
from numpy import loadtxt
import glob, os
from astropy.time import Time

try:
    import yaml
    with open('./config/database.yaml','r') as fin:
        db_config = yaml.load(fin)
    connection = mysql.connector.connect(**db_config)
    mySql_insert_query = """INSERT INTO candidates (id, x_coor, y_coor, RA, Decl, mag, mag_err, FWHM, ellip, flag, mjd)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s) """

    os.chdir("/home/mumak/pipeline/result/")
    for file in glob.glob("ID_*"):
	records_to_insert1 = loadtxt(file, dtype={'names': ('id', 'x_coor', 'y_coor', 'RA', 'Decl', 'mag', 'mag_err', 'FWHM', 'ellip','flag'),
                    'formats': ('S60', 'f', 'f','f', 'f','f','f','f', 'f', 'i2')})

        if records_to_insert1 is not None:
            date = file[4:8] + "-" + file[8:10] + "-" + file[10:12] + "T00:00:00.000"
            time = Time(date, format='isot')
            records_to_insert1=records_to_insert1.tolist()

            if isinstance(records_to_insert1, tuple):
                records_to_insert1 = [records_to_insert1]
            records_to_insert = []
            for element in records_to_insert1:
                element = list(element)
                element.append(time.mjd)
                element = tuple(element)
                records_to_insert.append(element)

            cursor = connection.cursor()

            cursor.executemany(mySql_insert_query, records_to_insert)
            connection.commit()
            print(cursor.rowcount, "Record inserted successfully into target table")

except mysql.connector.Error as error:
    print(file)
    print("Failed to insert record into MySQL table {}".format(error))

"""
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
"""
