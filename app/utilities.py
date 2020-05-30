from flask import flash


def flash_info(message):
    flash(message, "info")


def flash_error(message):
    flash(message, "danger")


def flash_success(message):
    flash(message, "success")
