import os
import ovation.jar

CLASSPATH = [os.path.expanduser(os.path.join(ovation.jar.jar_directory(), 'ovation.jar'))]
os.environ["CLASSPATH"] = os.path.pathsep.join(CLASSPATH)


from jnius import autoclass, cast, JavaException
