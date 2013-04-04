#!/usr/bin/python
import os, sqlite3, glob, argparse
import yaml 

def importCode(db, path, tblName='code'):
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE %s (filename VARCHAR, code VARCHAR, description VARCHAR)" % tblName)
    # if this generates an error then we should suspect table already exists

    path = os.path.join(path, '*.py')
    files = []
    for filePath in glob.glob(path):
        desc = raw_input("Enter the description for '%s': " % filePath)
        with open(filePath) as f:
            #files.append( ( sqlite3.Binary(f.read()) , desc ) )
            files.append( ( os.path.basename(filePath), f.read() , desc ) )

    con.executemany("INSERT INTO %s VALUES(?,?,?)" % tblName, files)
    con.commit()

dataTypes = {'str':'TEXT', 'int':'INTEGER', 'raw':'BLOB'}

def buildTable(con, tableName, tableDict):
    createStmt = "CREATE TABLE %s (" % tableName
    constraintStr = ""
    for colName in tableDict:
        print colName
        colDict = tableDict[colName]

        # setup datatype
        dataType = colDict['datatype']
        if dataType in dataTypes:
            dataType = dataTypes[dataType]
        colStr = "%s %s" % (colName, dataType)

        # determine if primary key
        if 'primary_key' in colDict:
            colStr = colStr + " PRIMARY KEY"
        elif 'foreign_key' in colDict:
            foreignTable, foreignCol = colDict['foreign_key'].split('.')
            constraintStr = constraintStr + ", FOREIGN KEY(%s) REFERENCES %s(%s)" % (colName, foreignTable, foreignCol) 

        # determine if unique
        if 'unique' in colDict:
            colStr = colStr + " UNIQUE"

        createStmt = createStmt + colStr + ", "
    
    createStmt = createStmt[:-2] + constraintStr + ")"
    print createStmt

    try:
        con.execute(createStmt)
    except:
        print "Error creating the '%s' table" % tableName
        print "Here is the parsed sql create statement:\n%s" % createStmt 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Adds python code to sqlite database')
    parser.add_argument('yaml', type=str, help='The path to the yaml file with the table structures')
    parser.add_argument('-db', type=str, default='db.sqlite',  help='The database having python code added')

    args = parser.parse_args()
    with open(args.yaml) as f:
        schemaDict = yaml.load(f)
    
    con = sqlite3.connect(args.db)

    for tableName in schemaDict: # each one of these is a dictionary with table structure
        print tableName, schemaDict[tableName]
        buildTable(con, tableName, schemaDict[tableName])

    con.commit()
