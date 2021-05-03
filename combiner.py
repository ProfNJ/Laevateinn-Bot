import fileinput
import glob
import os

file_list = glob.glob('./en/*.fe0db')

if (os.path.isfile('./db.csv') == False):
    with open('db.csv','w', encoding='utf-8') as file:
        input_lines = fileinput.input(file_list,  openhook=fileinput.hook_encoded("utf-8"))
        file.writelines('card_number,set,card_code,name_jp,name_eng,deploy_cost,promote_cost,base,class,color,gender,weapon,type,attack,support,range,effect,ext1,ext2,ext3')
        file.writelines(input_lines)