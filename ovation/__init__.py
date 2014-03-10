import os
import glob

# Follow Matlab APIs NewDataContext here...

jars_directory = os.path.join(os.path.dirname(__file__), 'jars')
CLASSPATH = []
for jar_path in glob.iglob(os.path.join(jars_directory, "*.jar")):
    CLASSPATH.append(jar_path)

os.environ["CLASSPATH"] = os.path.pathsep.join(CLASSPATH)

from jnius import autoclass, cast, JavaException


JAR_DIRS = {
    "osx" : "~/Library/Application Support/us.physion.ovation/python",
    "windows" : "",
    "linux" : "~/.ovation/python"
}


