from . import sandbox
from . import python_sandbox

def create_images():
    sandbox.module_init_called = True
    # create images
    print("creating docker image for c/C++ tests ...")
    sandbox.CppImage(None).get_container('/', 'ls')
    print("done")
    print("creating docker image for java tests ...")
    sandbox.JavaImage(None).get_container('/', 'ls')
    print("done")
    print("creating docker image for python tests ...")
#    python_sandbox.PythonImage(None).get_container('/')
    print("done")

#if __name__ == '__main__':
#    create_images()


