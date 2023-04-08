#!/bin/bash

# Change the directory to your Django project's root directory
cd /var/app

# Start Daphne with the ASGI application for the ix project
daphne -b 0.0.0.0 -p 8000 ix.server.asgi:application
