import os
import openai
import argparse
from pdfminer.high_level import extract_text

with open(os.path.expanduser(".openai_api.txt"), "r") as f:
    openai.api_key = f.read().strip()

prompt = "与えられた論文の要点をまとめ、以下の項目で日本語で出力せよ。それぞれの項目は最大でも180文字以内に要約せよ。"

import re

def remove_sections(text):
    text = re.sub(r'(?is)references.*?abstract', ' ', text)
    text = re.sub(r'(?is)acknowledgement.*', ' ', text)
    text = re.sub(r'(?is)acknowledgements.*', ' ', text)
    return text

def get_summary(text):
    print("### input text", text)
    response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': text}
                ],
                temperature=0.25,
            )
    summary = response['choices'][0]['message']['content']
    print("#### GPT", summary)
    dict = {}    
    for b in summary.split('\n'):
        print("****", b)
        if b.startswith("論文名"):
            dict['title_jp'] = b[4:].lstrip()
        if b.startswith("キーワード"):
            dict['keywords'] = b[6:].lstrip()
        if b.startswith("課題"):
            dict['problem'] = b[3:].lstrip()
        if b.startswith("手法"):
            dict['method'] = b[3:].lstrip()
        if b.startswith("結果"):
            dict['result'] = b[3:].lstrip()
    print("Dict by ChatGPT", dict)
    return dict

def main(pdf_filepath):
    text = extract_text(pdf_filepath)
    dict = get_summary(text)
    
    xml = dicttoxml.dicttoxml(dict, attr_type=False, root=False).decode('utf-8')
    xml = minidom.parseString(xml).toprettyxml(indent="   ")
    print("###########\n", xml, "\n#######")

    dirpath, _ = os.path.split(pdf_filepath)
    with open(f"{dirpath}/summary.xml", "w") as f:
        f.write(xml)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_filepath', help='path to the PDF file')
    args = parser.parse_args()

    print(args)

    main(pdf_filepath=args.pdf_filepath)
