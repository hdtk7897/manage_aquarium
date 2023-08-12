#!/bin/sh
echo "temp:"${1}
token=pY5mO6MnPlFt9q66FiG6QAWtUfwcyIN2KF5l1eFdoq9
message="temparature:"${1}

curl https://notify-api.line.me/api/notify \
  -H "accept: application/json" \
  -H "Authorization:Bearer $token" \
   -d "message="$message
