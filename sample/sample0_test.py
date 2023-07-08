import requests
domain = "http://127.0.0.1:5000/api/v1"

req = requests.get("%s/todos" % domain)
print(req.status_code)
print(req.text)
print(req.headers['content-type'])

req = requests.post("%s/todo" % domain, data={'title': 'supertitle', 'description': 'superdescription'})
print(req.status_code)
print(req.text)
print(req.headers['content-type'])

req = requests.get("%s/todo/1" % domain)
print(req.status_code)
print(req.text)
print(req.headers['content-type'])

req = requests.put("%s/todo/1" % domain, data={'id': 1, 'title': 'supertitle vraiment super', 'description': 'superdescription super', 'status': 'open'})
print(req.status_code)
print(req.text)
print(req.headers['content-type'])

req = requests.patch("%s/todo/1" % domain, data={'title': 'title', 'status': 'closed'})
print(req.status_code)
print(req.text)
print(req.headers['content-type'])

req = requests.get("%s/todo/1" % domain)
print(req.status_code)
print(req.text)
print(req.headers['content-type'])

req = requests.delete("%s/todo/1" % domain)
print(req.status_code)
print(req.text)
print(req.headers['content-type'])
