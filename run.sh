#!/bin/bash

#local network from other computers can access the server
uvicorn main:app --reload --host
