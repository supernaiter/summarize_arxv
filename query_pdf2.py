import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pdfminer.high_level import extract_text
import openai
import argparse

# Add your API key to a file named .openai_api.txt
with open(".openai_api.txt", "r") as f:
    openai.api_key = f.read().strip()

def remove_unnecessary_parts(text):
    text = re.sub(r"(?is)\b(acknowledgments|acknowledgement|references)\b.*", "", text)
    text = re.sub(r"(?is)\bappendix\b.*", "", text)
    return text

def preprocess_text(text):
    # remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # tokenization
    words = word_tokenize(text)

    # remove stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    return " ".join(words)

def reduce_length_with_gpt35(text):
    prompt = "Summarize this paper into 8000 tokens or less:"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-16k",
        prompt=prompt + text
    )
    return response.choices[0].text.strip()

def generate_summary_with_gpt4(text):
    prompt = "この論文の要約を生成してください："
    response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': text}
                ],
                temperature=0.25,
            )
    summary = response['choices'][0]['message']['content']
    return summary

def main(pdf_filepath):
    # Extract text from PDF
    text = extract_text(pdf_filepath)

    # Remove unnecessary parts
    text = remove_unnecessary_parts(text)

    # Preprocess text
    text = preprocess_text(text)

    # If the text is too long, reduce it with GPT-3.5
    if len(text.split()) > 8000:
        text = reduce_length_with_gpt35(text)

    # Generate summary with GPT-4
    summary = generate_summary_with_gpt4(text)

    print(summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_filepath', help='path to the PDF file')
    args = parser.parse_args()
    main(pdf_filepath=args.pdf_filepath)
