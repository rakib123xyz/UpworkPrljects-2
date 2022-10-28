import  pandas as pd
import json

with open('Input/combinet.json', encoding="utf-8") as json_file:
    data = json.load(json_file)

file = open('Output/usernames.txt', encoding="utf-8", mode="x")




usernames =[]

for section in data:

    layouts = section["sections"]
    for layout in layouts:
        medias = layout["layout_content"]["medias"]
        for media in medias:
            row = {"UserName": ""}
            username = media["media"]["user"]["username"]
            usernames.append(username)


print(len(usernames))
res = list(set(usernames))
print(len(res))

for line in res:
    file.writelines(line +",")




