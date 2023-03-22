from aqt import mw

"""
def gc(arg, fail=False):
    conf =  mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    else:
        return fail
		
		
		import sys

"""

from aqt import mw

userOption = None


def getUserOption(key=None, default=None):
    global userOption
    if userOption is None:
        userOption = mw.addonManager.getConfig(__name__)
    if key is None:
        return userOption
    if key in userOption:
        return userOption[key]
    else:
        userOption[key] = default
        writeConfig()
        return default


def writeConfig():
    mw.addonManager.writeConfig(__name__, userOption)


def update(_):
    global userOption, fromName
    userOption = None
    fromName = None


mw.addonManager.setConfigUpdatedAction(__name__, update)

fromName = None


def getFromName(name):
    global fromName
    if fromName is None:
        fromName = dict()
        for dic in getUserOption("columns"):
            fromName[dic["name"]] = dic
    return fromName.get(name)

