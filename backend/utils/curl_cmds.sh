# metrics creation
curl -i -X POST 127.0.0.1:9999/metrics/ -H "Content-Type: application/json" -d '{"metrics": [{"revision": 123456, "filename": "/my/first/file", "mccabe": 125, "comments": 12, "sloc": 1000}]}'
curl -i -X POST 127.0.0.1:9999/metrics/ -H "Content-Type: application/json" -d '{"metrics": [{"revision": 1234567, "filename": "/my/first/file", "mccabe": 125, "comments": 12, "sloc": 1000}, {"revision": 1234567, "filename": "/my/other/file", "mccabe": 125, "comments": 12, "sloc": 1000}]}'

# LIST MODIFICATION
curl -i -X PUT 127.0.0.1:9999/lists/1 -H "Content-Type: application/json" -d '{"name":"list number33"}'

# metrics retrival
curl -i 127.0.0.1:9999/metrics/42096
curl -i 127.0.0.1:9999/metrics/1234567/sloc/mccabe


# lastrevision
curl -i 127.0.0.1:9999/lastrevision








# ITEM CREATION
curl -i -X POST 127.0.0.1:9999/lists/1/items/ -H "Content-Type: application/json" -d '{"name":"new list item"}'

# ITEM MODIFICATION
curl -i -X PUT 127.0.0.1:9999/lists/1/items/1 -H "Content-Type: application/json" -d '{"name":"item 1 "}'

# ITEM RETRIEVAL
curl -i 127.0.0.1:9999/lists/1/items/
curl -i 127.0.0.1:9999/lists/1/items/1

