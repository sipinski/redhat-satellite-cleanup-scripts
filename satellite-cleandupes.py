#!/usr/bin/python
#
# This script connects to satellites postgres database and find registered (content) hosts that have
# multiple registrations, and then deletes older/obsoleted registrations using the satellite API tool (hammer).
#
# sipinski 20170116
import psycopg2, sys, os

##
# Connect to Database
##

# foreman database password can be found in /etc/foreman/database.yml
try:
    conn = psycopg2.connect("dbname='foreman' user='foreman' host='localhost' password='changeme'")
except:
    print "Unable to connect to the database:"

# Get a cursor
cur = conn.cursor()

# Determine whether there are any duplicate registered systems to cleanup 
sqlNumDupes = """
    select count(*)
    from (
        select *, COUNT(*) over (partition by name) as ct 
        from katello_systems order by name,created_at desc) subrc 	
    where ct > 1
"""

try: 
    cur.execute(sqlNumDupes)
except:
    print "Unable to query for number of duplicate systems"
    sys.exit(1)

numDupes = cur.fetchone()

if (numDupes < 1):
   print "Nothing to clean up. Exiting."
   sys.exit(0)

##
# Get list of systems with duplicate registrations 
## 

sqlDupeSystems = """
    select uuid,created_at,name
        from (
            select *, ROW_NUMBER() over (partition by name) as cr
            from (
                select *, COUNT(*) over (partition by name) as ct
                from katello_systems order by name,created_at desc) subrc
            ) subrn
        where ct > 1
"""

print "Cleaning up the following list of duplicates: "
try:
    cur.execute(sqlDupeSystems); 
except: 
    print "Unable to query for list of duplicate systems"
    sys.exit(1)

rows = cur.fetchall()

for row in rows: 
    print " %s  %s  %s " % (row[0], row[1], row[2])

print "Total number of duplicate entries %d" % numDupes


##
# Get list of systems with duplicate registrations to be removed
## 

print "\nRemoving the following duplicate systems:" 

sqlDupeSystemsToRemove = """
    select uuid,created_at,name
        from (
            select *, ROW_NUMBER() over (partition by name) as cr
            from (
                select *, COUNT(*) over (partition by name) as ct
                from katello_systems order by name,created_at desc) subrc
            ) subrn
        where ct > 1 and cr >1
"""

try:
    cur.execute(sqlDupeSystemsToRemove)
except:
    print "Unable to query for list of duplicate systems to remove"
    sys.exit(1)

rows = cur.fetchall()

for row in rows: 
    print " %s  %s  %s " % (row[0], row[1], row[2])
    print "hammer content-host delete --id " , row[0]
    if os.system("hammer content-host delete --id"+ row[0]) != 0 :
        print "Aborting: Removing host ", row[0], " generated an error" 
        sys.exit(1)


print "Cleanup successful"
sys.exit(0)
