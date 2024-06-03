# coding=utf-8

import docker
import os
import time

start_time = time.time()
client = docker.from_env()
# print(client.version())

#image, build_logs = client.images.build(**your_build_kwargs)
#for chunk in build_logs:
#    if 'stream' in chunk:
#        for line in chunk['stream'].splitlines():
#            log.debug(line)

# print(client.images.list())

print("--- connect to docker dameon %s seconds ---" % (time.time() - start_time))
start_time = time.time()
print("create container")
volumes = ['/home/karin/docker/docker-sandbox-executor/solution/:/solution'
#           ,'/var/run/docker.sock:/var/run/docker.sock'
           ]
container = client.containers.create(image="docker-sandbox-praktomat_sandbox", volumes=volumes)
print(container)
print("start container")
container.start()
log = container.logs()
#exitcode, log = container.exec_run('ls')
print(type(log))
str_log = log.decode('UTF-8')
str_log = str_log.replace('\n', '\r\n')
print(str_log)

print("stop container")
container.stop()

print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()

print("get result")
tar, dict = container.get_archive("/sandbox/__result__")
print(dict)
with open("result.tar", 'bw') as f:
    for block in tar:
        f.write(block)


os.system("tar -xf result.tar")

print("remove container")
container.remove()

print("--- Cleanup %s seconds ---" % (time.time() - start_time))
#log = client.containers.run(image="docker-praktomat-praktomat_sandbox")
#print(type(log))
#str_log = log.decode('UTF-8')
#str_log = str_log.replace('\n', '\r\n')
#print(str_log)


