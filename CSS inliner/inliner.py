import premailer
import css_inline
import pandas as pd
import json
import csv
import htmlmin


inlineCss = css_inline.CSSInliner(remove_style_tags=True)


#converting to json---------------------------------------------------------
def csv_to_Json(csv_file):
    csv_file_path = csv_file

    products_dataframe = pd.read_csv(csv_file_path, sep="\t",encoding='utf-8',engine='python')
    products_json= products_dataframe.to_json(indent=2, orient="records")
    products_dict= json.loads(products_json)
    return products_dict

def dict_to_Csv(dictionary,csv_file_path):
    distination = str(csv_file_path)
    df = pd.DataFrame.from_dict(dictionary)

    csv = df.to_csv(distination,sep="\t", index=False , encoding='utf-8',engine='python')
    df.to_csv()
    return "successful"

def list_to_csv(list,csv_file_path):
    data= list
    ser = pd.Series(list)
    csv =ser.to_csv(csv_file_path,sep="\t",index=False, encoding='utf-8')
    return "successful"


def inliner(input_filepath):
    list=[]
    load = csv_to_Json(input_filepath)
    for x in range(len(load)):
        dict=[]
        body = load[x]["Description"]
        if body!=None:
            #row = premailer.transform(body,pretty_print=False)
           # minified = htmlmin.minify(row)
            row = inlineCss.inline(body)
            minified = htmlmin.minify(row)
            list.append(minified)
        else:
            row =""
            list.append(row)
        print(x)
    return list

data = inliner("Asda discription.csv")
list_to_csv(data, "asda inlineed.csv")
