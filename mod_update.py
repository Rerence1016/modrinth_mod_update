from packaging.version import parse
import requests
import zipfile
import hashlib
import shutil
import json
import os
import re

# Hard coded values (customizable according to taste)
TEMP_DIR = "mod_update-temp"
JSON_FILE_NAME = "mods"
TARGET_MINECRAFT_VERSION = '1.21.4'
LOADER = 'fabric'

# Necessary variables for connection to Modrinth
MODRINTH_API_VERSION = 2
MODRINTH_URL = f"https://api.modrinth.com/v{MODRINTH_API_VERSION}"
header = {'User-Agent': "modrinth_mod_update.py (Rerence1016 on GitHub)"}


# Custom functions
# Avoids repetitive code!

# HTTP code handling
def HTTP_code_handling(HTTP_request: int):
	if (HTTP_request == 410):
		print(f"{HTTP_request}: WARNING: MODRINTH API HAS BEEN DEPRECATED! PLEASE USE WHATEVER IS NEW!!")
	elif (HTTP_request == 404):
		print(f"{HTTP_request}: ID OR SLUG IS INVALID: PROJECT NOT FOUND!!")
	elif (HTTP_request == 200):
		# Success
		pass
	else:
		print(f"{HTTP_request}: SOME ERROR HAS HAPPENED (IDK)")

# Strip filenames to just versions with RegEx
# RegEx is hard coded for only Minecraft version 1.21.4, sadly
# You can change it here manually!
def clean_version(string_to_clean: str):
	cleaned = re.sub(r'(1\.21\.4)|(\.jar)', '', string_to_clean)
	cleaned = re.search(r'[\d\.]{3,}', cleaned)
	cleaned_version = cleaned.group()
	return cleaned_version


# A - Initial startup

# Detect if .json already exists
if f"{JSON_FILE_NAME}.json" not in os.listdir("."):
	# No .json detected (has to be explicitly named according to `JSON_FILE_NAME`)
	print(f"NO \"{JSON_FILE_NAME}.json\" DETECTED!")
	print("Making new one...")
	mods = {}
	MODS_FOLDER_PATH = input("Please type what folder your mods are located in: \n")
	ABSOLUTE_MOD_PATH = f"{os.path.abspath(MODS_FOLDER_PATH)}"
	os.chdir(ABSOLUTE_MOD_PATH)
	folder_mods = os.listdir(f"{ABSOLUTE_MOD_PATH}")
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	print(f"Mods found in \"{MODS_FOLDER_PATH}/\":\n")

	# Obtain version and slug from existing files in a directory
	for mod in folder_mods:
		with zipfile.ZipFile(f"{ABSOLUTE_MOD_PATH}/{mod}", 'r') as modfile:
			modfile.extract("fabric.mod.json", f"{TEMP_DIR}/")
		os.rename(f"{TEMP_DIR}/fabric.mod.json", f"{TEMP_DIR}/{mod}.json")
		mod_json = json.load(open(f"{TEMP_DIR}/{mod}.json"))
		mod_name = mod_json["name"]

		# Parameters for searching mods from existing files, i.e., connect them to Modrinth
		params = {'query': f"{mod_name}"}
		PROJECT_GET = requests.get(f"{MODRINTH_URL}/search", headers=header, params=params)
		HTTP_code_handling(PROJECT_GET.status_code)
		results = json.loads(PROJECT_GET.text)
		
		# Setting JSON files
		version = clean_version(mod)
		slug = results["hits"][0]["slug"]
		path = f"{ABSOLUTE_MOD_PATH}/{mod}"

		print(f"Filename: {mod} \n\tName: {mod_name} \n\tSlug: {slug} \n\tVersion: {version} \n")
		mods[f"{slug}"] = {"name": f"{mod_name}", "slug": f"{slug}", "version": f"{version}", "path": f"{path}"}
	
	mods["mods_folder_path"] = f"{ABSOLUTE_MOD_PATH}"
	# Write to .json file
	MOD_INFO_JSON = json.dumps(mods, indent=4)
	MODS_JSON = open(f"{JSON_FILE_NAME}.json", 'w')
	MODS_JSON = MODS_JSON.write(MOD_INFO_JSON)

	# Open .json file
	# Not putting all the code in a `with as` statement to make it less confusing
	MODS_JSON = open(f"{JSON_FILE_NAME}.json")
	MODS_JSON = MODS_JSON.read()
	MODS_JSON = json.loads(MODS_JSON)

	print(f"Mod info has been written to {JSON_FILE_NAME}.json: Successful \n")
	path = MODS_JSON["mods_folder_path"]
	shutil.rmtree(f"{TEMP_DIR}")
	print("Deleted temp folder... \n")
else:
	# .json is detected
	print(f"Detected {JSON_FILE_NAME}.json! \n")
	MODS_JSON = open(f"{JSON_FILE_NAME}.json")
	MODS_JSON = MODS_JSON.read()
	MODS_JSON = json.loads(MODS_JSON)

MODS_FOLDER_PATH = MODS_JSON["mods_folder_path"]


# B - Check for latest version, and compare against existing versions

# Parameters for GET request
params = {'loaders': f"{LOADER}", 'game_versions': f"{TARGET_MINECRAFT_VERSION}"}

# Iterate through all mods in .json
# Check for latest version on Modrinth

index_number = 0
mod_order = 1
for mod in MODS_JSON:
	if mod == "mods_folder_path":
		print(f"\nEnd of list in {JSON_FILE_NAME}.json! Mod updates completed!")
		break
	else:
		PROJECT_SLUG = MODS_JSON[mod]["slug"]
		ABSOLUTE_MOD_PATH = MODS_JSON[mod]["path"]
		mod_version = MODS_JSON[mod]["version"]

	PROJECT_GET = requests.get(f"{MODRINTH_URL}/project/{PROJECT_SLUG}/version", headers=header, params=params)

	HTTP_code_handling(PROJECT_GET.status_code)

	MODRINTH_JSON = json.loads(PROJECT_GET.text)
	
	# Find latest mod version with proper Minecraft version and mod loader support
	for versions in MODRINTH_JSON:
		if TARGET_MINECRAFT_VERSION not in MODRINTH_JSON[index_number]["game_versions"]:
			index_number += 1
			continue
		else:
			if LOADER not in MODRINTH_JSON[index_number]["loaders"]:
				index_number += 1
				continue
			else:
				latest_version = MODRINTH_JSON[index_number]["version_number"]
				latest_version = clean_version(latest_version)
				print(f"\nVersion {latest_version} detected for Minecraft {TARGET_MINECRAFT_VERSION}")
				break

	# Compare latest version against existing version
	if True:
		mod_version = parse(str(mod_version))
		latest_version = parse(latest_version)
		# If same version
		same_version = ""
		if mod_version < latest_version:
			status = "newer than"
		elif mod_version > latest_version:
			status = "older than"
		elif mod_version == latest_version:
			status = "the same version as"
			same_version = f"No newer version than {mod_version}, nothing to do!\n"
		print(f"{mod_order}. {mod} -> {mod_version}\n\t"
			  f"{latest_version} is {status} {mod_version}!"
			  f"\n\t{same_version}")
					

		# C - Download newer mod files
					
		# If not the same version
		if same_version == "":

			# Values from JSON about file to download
			url = MODRINTH_JSON[index_number]["files"][0]["url"]
			filename = MODRINTH_JSON[index_number]["files"][0]["filename"]
			sha1_hash = MODRINTH_JSON[index_number]["files"][0]["hashes"]["sha1"]

			# Download from URL and write to file
			print(f"\tDownloading \"{mod}\" version {latest_version}...")
			response = requests.get(url, stream=True)
			with open(f"{filename}", mode="wb") as file:
				for chunk in response.iter_content(chunk_size=10*1024):
					file.write(chunk)
			print(f"\tDownload of \"{filename}\" successful!")

			# Verify checksum
			with open(f"{filename}", mode="rb") as file:
				file_hash = hashlib.file_digest(file, "sha1")
				file_hash = file_hash.hexdigest()
				print(f"\tTesting SHA1 checksum of \"{filename}\"...")

				# Checksum matches
				if file_hash == sha1_hash:
					print("\tChecksum matches! Mod's file integrity confirmed")
					os.remove(f"{ABSOLUTE_MOD_PATH}")
					os.replace(f"{filename}", f"{MODS_FOLDER_PATH}/{filename}")
					print("\tRemoved original file")

					# Writing new values to JSON
					MODS_JSON[mod]["version"] = f"{latest_version}"
					MODS_JSON[mod]["path"] = os.path.abspath(f"{MODS_FOLDER_PATH}/{filename}")
					with open(f"{JSON_FILE_NAME}.json", 'w') as file:
						json.dump(MODS_JSON, file, indent=4)
						print(f"\tUpdated \"{JSON_FILE_NAME}.json\"!")

				# Checksum fails
				else:
					print("\tChecksum doesn't match, file may be corrupted!")
					print("\tKeeping original file...")
					os.remove(f"{filename}")
					
	mod_order += 1
	index_number = 0