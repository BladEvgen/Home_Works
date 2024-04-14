@echo off
call ..\.venv\Scripts\activate


sanic main:app --host=0.0.0.0 --port=1337 --fast -r --debug
