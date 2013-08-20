import json, requests, sqlite3

url = 'http://localhost:9000/api/commands'

"""Test Create"""
params = dict(
    name='testCreateName',
    description='testCreateDescription',
    module='testCreateModule',
    command='testCreateCommand'
)

resp = requests.post(url=url, params=params)
data = resp.json()

id = data[0]

if(data[1] == 'testCreateName'):
    print "Test create: passed"
else:
    print "Test create: failed"


"""Test Read with ID that exists"""
params = dict(
    id=str(id)
)

resp = requests.get(url=url, params=params)
data = resp.json()

if(data[1] == 'testCreateName'):
    print "Test read: passed"
else:
    print "Test read: failed"


"""Test Read with ID that does not exist"""
params = dict(
    id='5708709'
)

resp = requests.get(url=url, params=params)
data = resp.json()

if(str(data) == 'None'):
    print "Test read (with bad id): passed"
else:
    print "Test read (with bad id): failed"


"""Test Update with ID that exists"""
params = dict(
    id=str(id),
    name='testUpdateName',
    description='testUpdateDescription',
    module='testUpdateModule',
    command='testUpdateCommand'
)

resp = requests.put(url=url, params=params)
data = resp.json()

if(data[1] == 'testUpdateName'):
    print "Test update: passed"
else:
    print "Test update: failed"


"""Test Update with ID that does not exist"""
params = dict(
    id='2340985',
    name='testUpdateNewName',
    description='testUpdateNewDescription',
    module='testUpdateNewModule',
    command='testUpdateNewCommand'
)

resp = requests.put(url=url, params=params)
data = resp.json()

if(data[1] == 'testUpdateNewName'):
    print "Test update (with new ID): passed"
else:
    print "Test update (with new ID): failed"
    

"""Test Delete"""
params = dict(
    id='2340985'
)

requests.delete(url=url, params=params)

resp = requests.get(url=url, params=params)
data = resp.json()

if(str(data) == 'None'):
    print "Test delete: passed"
else:
    print "Test delete: failed"


"""Test Read with empty string for ID"""
params = dict(
    id=''
)

resp = requests.get(url=url, params=params)
data = resp.json()

if(str(data) == 'None'):
    print "Test read (with empty string): passed"
else:
    print "Test read (with empty string): failed"
    
    
"""Test Read with non integer ID"""
params = dict(
    id='test'
)

resp = requests.get(url=url, params=params)
data = resp.json()

if(str(data) == 'None'):
    print "Test read (with non integer ID): passed"
else:
    print "Test read (with non integer ID): failed"    
    
    
"""Test Update with empty string for ID"""
params = dict(
    id='',
    name='testUpdateNewName',
    description='testUpdateNewDescription',
    module='testUpdateNewModule',
    command='testUpdateNewCommand'
)

resp = requests.put(url=url, params=params)
data = resp.json()

if(str(data) == 'None'):
    print "Test update (with empty string): passed"
else:
    print "Test update (with empty string): failed"
    
    
"""Test Update with non integer ID"""
params = dict(
    id='test',
    name='testUpdateNewName',
    description='testUpdateNewDescription',
    module='testUpdateNewModule',
    command='testUpdateNewCommand'
)

resp = requests.put(url=url, params=params)
data = resp.json()

if(str(data) == 'None'):
    print "Test update (with non integer ID): passed"
else:
    print "Test update (with non integer ID): failed"


"""Test Delete with empty string for ID"""
params = dict(
    id=''
)

conn = sqlite3.connect('commands.db')
with conn:
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM Commands")
    numRows = cur.fetchone()
    requests.delete(url=url, params=params)
    cur.execute("SELECT Count(*) FROM Commands")
    numRowsAfter = cur.fetchone()

if (numRows == numRowsAfter):
    print "Test delete (with empty string): passed"
else:
    print "Test delete (with empty string): failed" 
    
    
"""Test Delete with non integer ID"""
params = dict(
    id='test'
)

conn = sqlite3.connect('commands.db')
with conn:
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM Commands")
    numRows = cur.fetchone()
    requests.delete(url=url, params=params)
    cur.execute("SELECT Count(*) FROM Commands")    
    numRowsAfter = cur.fetchone()

if (numRows == numRowsAfter):
    print "Test delete (with non integer ID): passed"
else:
    print "Test delete (with non integer ID): failed"   

"""Clean up"""
params = dict(
    id=str(id)
)

requests.delete(url=url, params=params)

conn = sqlite3.connect('commands.db')
with conn:
    cur = conn.cursor()
 
    cur.execute("delete from sqlite_sequence where name='Commands'")         