from star import Star, star_iterator
import mysql
import mysql.connector
import logging
import re
from collections import defaultdict
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s') 
logger = logging.getLogger()

import argparse
parser = argparse.ArgumentParser(description='Process some integers.')

subparsers = parser.add_subparsers(dest='command')
subparser_update = subparsers.add_parser('update')
subparser_update.add_argument('--date', dest='date', default=None, required=True, help='which date to update.')
subparser_update.add_argument('--display_freq', dest='dispfreq', default=500, help='how often to display log info.')
subparser_info = subparsers.add_parser('info')
subparser_info.add_argument('--display_freq', dest='dispfreq', default=200000, help='how often to display log info.')
args = parser.parse_args()

def info():
    dicA = defaultdict(int)
    dicB = defaultdict(int)
        
    try:
        import yaml
        with open('../config/database.yaml','r') as fin:
            db_config = yaml.load(fin)
        logger.info("Try to establish connection")
        logger.info(str(db_config))
        connection = mysql.connector.connect(**db_config)
        logger.info("Connection established.")
    except mysql.connector.Error as e:
        logger.error("Error: {}".format(e))
        exit(0)
    cursor = connection.cursor()

    for idx, (sid, p) in enumerate(star_iterator()):
        if idx % args.dispfreq == 0:
            logger.info("PROGREE A-%d..." % idx)
        dicA[sid[1:9]] += 1

    mysql_select_query = "select id from supernovae"
    cursor.execute(mysql_select_query)
    rows = cursor.fetchall()
    for (sid,) in rows:
        if idx % args.dispfreq == 0:
            logger.info("PROGREE B-%d..." % idx)
        dicB[sid[1:9]] += 1
    connection.close()
    logger.info('% 10s % 8s % 8s' %('date', 'local', 'database'))
    for w in sorted(list(set.union(set(dicA.keys()), set(dicB.keys())))):
        if dicA[w] != dicB[w]:
            logger.info('\033[31m% 10s % 8d % 8d\033[0m' %(w, dicA[w], dicB[w]))
        else:
            logger.info('% 10s % 8d % 8d' %(w, dicA[w], dicB[w]))
    exit()


def update():
    if not re.match(r'\d{6}', args.date) or args.date is None:
        logger.warn('Please input date.')

    try:
        import yaml
        with open('../config/database.yaml','r') as fin:
            db_config = yaml.load(fin)
        logger.info("Try to establish connection")
        logger.info(str(db_config))
        connection = mysql.connector.connect(**db_config)
        logger.info("Connection established.")
    except mysql.connector.Error as e:
        logger.error("Error: {}".format(e))
        exit(0)

    cursor = connection.cursor()
    if args.date is None:
        logger.info("Clear old data.")
        mysql_select_query = "delete from supernovae"
        cursor.execute(mysql_select_query)
        logger.info("Clear complete.")
    else:
        logger.info("Clear data %s." % args.date)
        mysql_select_query = "delete from supernovae where id like '%%%s%%'" % args.date
        rc = cursor.execute(mysql_select_query)
        logger.info("Clear complete, %d rows affected." % cursor.rowcount)
    try:
        connection.commit()
    except Exception as e:
        connection.rollback()
        logger.error("Error occur %s."%e)

    for idx, (sname, spath) in enumerate(star_iterator(args.date)):
        if idx and idx % args.dispfreq == 0:
            try:
                connection.commit()
            except Exception as e:
                connection.rollback()
                logger.error("Error occur %s."%e)
            logger.info("#%d, %s" % (idx, sname))
        star = Star(sname, spath)
        p = star.properties
        tag, details = star.test()
        sql = 'INSERT INTO supernovae(id, tag, details, ratio_today, ratio_yesterday, quality, similarity, brightness_today, brightness_yesterday, brightness_shift) values ("%s", "%s", "%s", %s, %s, %s, %s, %s, %s, %s)' % (sname, tag, details, p['ratio'][1], p['ratio'][0], p['quality'], p['similarity'], p['brightness'][1], p['brightness'][0], p['brightness_shift'])
        cursor.execute(sql)
    try:
        connection.commit()
    except Exception as e:
        connection.rollback()
        logger.error("Error occur %s."%e)
    connection.close()

if __name__ == '__main__':
    if args.command == 'update':
        update()
    elif args.command == 'info':
        info()
        
