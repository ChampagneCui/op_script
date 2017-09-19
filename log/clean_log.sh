#!/bin/bash
 
find /opt/log/ -type f -mtime +3 -exec rm -rf {} \;
