#!/bin/bash

socat TCP-LISTEN:5555,fork,reuseaddr,bind=0.0.0.0 EXEC:"/app/sh_elf.sh"
