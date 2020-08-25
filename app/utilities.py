import os
from flask import flash
from zipfile import ZipFile


def flash_info(message):
    flash(message, "info")


def flash_error(message):
    flash(message, "danger")


def flash_success(message):
    flash(message, "success")


def is_extension_allowed(filename: str, allowed_extensions: list):
    return filename.split('.')[-1].lower() in allowed_extensions


def handle_uploaded_file(filename: str, allowed_extensions: list):
    if filename.endswith('zip'):
        with ZipFile(filename) as myzip:
            namelist = myzip.namelist()
            if len(myzip.namelist()) > 1:
                raise Exception("Too many files in zip file {}".format(filename))
            file_in_zip = namelist[-1]
            if not is_extension_allowed(file_in_zip, allowed_extensions):
                raise Exception("Not allowed file extension")
            return myzip.extract(member=file_in_zip, path=os.path.dirname(filename))

    if not is_extension_allowed(filename, allowed_extensions):
        raise Exception("Not allowed file extension")
    else:
        return filename
