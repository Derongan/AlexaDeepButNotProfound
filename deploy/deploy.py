import os
import zipfile

import boto3

ALEXA_ZIP = "alexa_deploy"

ALEXA_LAMBDA = "DeepButNotProfoundAlexa"

ROOT = "../src"
LIB_ROOT = "../src/libs"

EXCLUDED_DIRS = [
    "__pycache__"
]

EXCLUDED_FILES = [
    "deploy.zip",
    "inspect_db.py",
    "setup_db.py"
]

EXCLUDED_DIRS_ALEXA = []

ALEXA_LIBS = []


def make_archive(zipname, exclude_dirs, exclude_files, root_dir, libs=()):
    with zipfile.ZipFile(zipname + ".zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file not in exclude_files:
                    archive.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), root_dir))

        for lib in libs:
            for root, dirs, files in os.walk(os.path.join(LIB_ROOT, lib)):
                for file in files:
                    archive.write(os.path.join(root, file),
                                  os.path.relpath(os.path.join(root, file), os.path.join(LIB_ROOT, lib)))


def deploy(zipname, funcname):
    with open(zipname + ".zip", "rb") as archive:
        client = boto3.client('lambda')

        vals = {
            "FunctionName": funcname,
            "ZipFile": archive.read()
        }
        client.update_function_code(**vals)


def make_archive_for_alexa():
    make_archive(ALEXA_ZIP, EXCLUDED_DIRS + EXCLUDED_DIRS_ALEXA, EXCLUDED_FILES, ROOT, ALEXA_LIBS)


def deploy_alexa():
    deploy(ALEXA_ZIP, ALEXA_LAMBDA)


if __name__ == "__main__":
    print("Deploying Alexa")
    make_archive_for_alexa()
    deploy_alexa()
