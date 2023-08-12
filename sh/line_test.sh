#!/bin/sh

url = "https://notify-api.line.me/api/notify" 
token = "pY5mO6MnPlFt9q66FiG6QAWtUfwcyIN2KF5l1eFdoq9"
headers = {"Authorization" : "Bearer "+ token} 
message =  "お魚テスト" 
payload = "message"${message} 
