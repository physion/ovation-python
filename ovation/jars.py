"""
Utilities for managing downloading and caching of Ovation JARs
"""


JAR_DIRS = {
    "osx" : "~/Library/Application Support/us.physion.ovation/python",
    "windows" : "",
    "linux" : "~/.ovation/python"
}

def jar_path():
    """
    Returns the path to the cached ovation-all-in-one JAR. Jar is downloaded
     if needed.
    """

