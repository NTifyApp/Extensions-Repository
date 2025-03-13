# This python script generates all the JSON files needed for the repository
import json
import os
import shutil
import subprocess
import sys
import urllib.request


ROOT_LOCATION = "repo/repo.json"
JARS_LOCATION = "repo/storage"
EXTENSIONS_LOCATION = "extensions"
BUILD_SCRIPT = "build.sh" # e.g. extensions/MSNStatusSupport/build.sh
SPXP_JAR_URL = "https://github.com/SpotifyXP/SpotifyXP/releases/latest/download/SpotifyXP.jar"
REPO_PATH = "repo"
DEPENDENCIES = []

def compile_jar(dir, PLUGIN_JSON):
    print("Building " + dir)
    os.chmod(os.path.join(EXTENSIONS_LOCATION + "/" + dir + "/" + BUILD_SCRIPT), 0o755)
    proc = subprocess.call("./" + BUILD_SCRIPT, cwd=EXTENSIONS_LOCATION + "/" + dir, shell=True)
    if proc != 0:
        print("Failed to build " + dir)
        sys.exit(-1)
    if os.path.exists(EXTENSIONS_LOCATION + "/" + dir + "/build.gradle"):
        JAR_PATH = EXTENSIONS_LOCATION + "/" + dir + "/build/libs/" + dir + ".jar"
        if not os.path.exists(JAR_PATH):
            print("Couldn't find jar file in '" + JAR_PATH + "'")
            sys.exit(-1)
        shutil.copyfile(JAR_PATH, JARS_LOCATION + "/" + dir + "-" + PLUGIN_JSON["author"] + ".jar")
    elif os.path.exists(EXTENSIONS_LOCATION + "/" + dir + "/pom.xml"):
        JAR_PATH = EXTENSIONS_LOCATION + "/" + dir + "/target/" + dir + ".jar"
        if not os.path.exists(JAR_PATH):
            print("Couldn't find jar file in '" + JAR_PATH + "'")
            sys.exit(-1)
        shutil.copyfile(JAR_PATH, JARS_LOCATION + "/" + dir + "-" + PLUGIN_JSON["author"] + ".jar")
    else:
        print("Extension named '" + dir + "' doesn't contain a recognized build system")
        sys.exit(-1)

def extract_extension_descriptor(dir):
    PLUGIN_JSON_PATH = EXTENSIONS_LOCATION + "/" + dir + "/src/main/resources/plugin.json"
    return json.loads(open(PLUGIN_JSON_PATH).read())

def create_plugin_descriptor(PLUGIN_JSON):
    NEW_PLUGIN_JSON = PLUGIN_JSON
    del NEW_PLUGIN_JSON["main"]
    NEW_PLUGIN_JSON["location"] = JARS_LOCATION + "/" + PLUGIN_JSON["name"] + "-" + PLUGIN_JSON["author"] + ".jar"
    for dependency in NEW_PLUGIN_JSON["dependencies"]:
        dependency["location"] = REPO_PATH + "/" + dependency["name"] + "-" + dependency["author"] + ".json"
        DEPENDENCIES.append(dependency)
    file = open(REPO_PATH + "/" + PLUGIN_JSON["name"] + "-" + PLUGIN_JSON["author"] + ".json", "w")
    file.write(json.dumps(NEW_PLUGIN_JSON))
    file.close()

# 1. Make required directories
if os.path.exists(REPO_PATH):
    shutil.rmtree(REPO_PATH)
    os.makedirs(REPO_PATH)
else:
    os.makedirs(REPO_PATH)

if not os.path.exists(JARS_LOCATION):
    os.makedirs(JARS_LOCATION)

# 2. Download the newest SpotifyXP.jar
if not os.path.exists(EXTENSIONS_LOCATION + "/SpotifyXP.jar"):
    print("Downloading SpotifyXP")
    urllib.request.urlretrieve(SPXP_JAR_URL, EXTENSIONS_LOCATION + "/SpotifyXP.jar")

# 3. Create repo.json
REPO_JSON = {
    "name": "SpotifyXP-Repository",
    "extensions": [
    ]
}

# 4. Build every extension via the build script defined in BUILD_SCRIPT
print("Building extensions")
for dir in os.listdir(EXTENSIONS_LOCATION):
    if dir.endswith(".jar"): continue

    # 4.1. Extract extension descriptor "plugin.json"
    PLUGIN_JSON = extract_extension_descriptor(dir)

    # 4.2. Compile and copy extension
    compile_jar(dir, PLUGIN_JSON)

    # 4.3 Create extension descriptor for the repository e.g. Test-Werwolf2303.json
    create_plugin_descriptor(PLUGIN_JSON)

    # 4.4 Add extension to the list
    REPO_JSON["extensions"].append({
        "location": "/" + PLUGIN_JSON["name"] + "-" + PLUGIN_JSON["author"] + ".json",
    })

# 5. Store repo.json
file = open(ROOT_LOCATION, "w")
file.write(json.dumps(REPO_JSON))
file.close()

# 6. Check for non existent dependencies
for dependency in DEPENDENCIES:
    if not os.path.exists(dependency["location"]):
        print("Couldn't find dependency '" + dependency["name"] + " from " + dependency["author"] + "'")
        sys.exit(-1)



