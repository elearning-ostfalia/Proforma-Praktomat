# coding=utf-8

import docker
import os
import time
import tarfile

start_time = time.time()
client = docker.from_env()
# print(client.version())

#image, build_logs = client.images.build(**your_build_kwargs)
#for chunk in build_logs:
#    if 'stream' in chunk:
#        for line in chunk['stream'].splitlines():
#            log.debug(line)

# print(client.images.list())



print("create container")
# start_time = time.time()
#volumes = ['/home/karin/docker/docker-sandbox-executor/solution/:/solution']
volumes = [] # todo
container = client.containers.create(image="python-praktomat_sandbox", volumes=volumes)
if container == None:
    raise Exception('could not create container')    
# print("--- create docker container  %s seconds ---" % (time.time() - start_time))
# print(container)



print("** start container")
# start_time = time.time()
container.start()
# print("--- start docker container  %s seconds ---" % (time.time() - start_time))

print("** create tar files and upload to sandbox")
# start_time = time.time()
with tarfile.open("task.tar", 'w:gz') as tar:
    tar.add("./task", arcname=".", recursive=True)    
with tarfile.open("solution.tar", 'w:gz') as tar:
    tar.add("./solution", arcname=".", recursive=True)    
with open('task.tar', 'rb') as fd:
    if not container.put_archive(path='/sandbox', data=fd):
        raise Exception('cannot put task-archive.tar')
with open('solution.tar', 'rb') as fd:
    if not container.put_archive(path='/sandbox', data=fd):
        raise Exception('cannot put solution-archive.tar')
#print("---upload tar files  %s seconds ---" % (time.time() - start_time))

# print(container.logs().decode('UTF-8').replace('\n', '\r\n'))

start_time = time.time()
code, str = container.exec_run("python3 /sandbox/run_suite.py")
print("---run test  %s seconds ---" % (time.time() - start_time))
print(code)
print("Test run log")
print(str.decode('UTF-8').replace('\n', '\r\n'))


# print("** get logs")
# print(container.logs().decode('UTF-8').replace('\n', '\r\n'))

print("** stop container")
start_time = time.time()
container.stop()
print("--- stop %s seconds ---" % (time.time() - start_time))
start_time = time.time()

print("** get result")
tar, dict = container.get_archive("/sandbox/__result__")
print(dict)
with open("result.tar", 'bw') as f:
    for block in tar:
        f.write(block)

print("** extract and list result")
with tarfile.open("result.tar", 'r') as tar:
    tar.extractall()

if os.path.exists("__result__/unittest_results.xml"):
    print("TEST RESULT AVAILABLE")
else:
    print("NO TEST RESULT AVAILABLE")

# os.system("ls -al __result__")

print("** remove container")
container.remove()

# print("--- Cleanup %s seconds ---" % (time.time() - start_time))
#log = client.containers.run(image="docker-praktomat-praktomat_sandbox")
#print(type(log))
#str_log = log.decode('UTF-8')
#str_log = str_log.replace('\n', '\r\n')
#print(str_log)


