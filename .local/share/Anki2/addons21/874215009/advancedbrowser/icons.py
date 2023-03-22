from aqt import *


def getQIcon(name):
    "Convenience method for getting a QIcon from this add-on's icon directory."
    here = os.path.dirname(os.path.realpath(__file__))
    iPath = os.path.join(here, "icons", name)
    return QIcon(iPath)
