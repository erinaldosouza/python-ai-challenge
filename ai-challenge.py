
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd 
import json

load_dotenv()

def request_file_content():
    response = requests.get("https://cdn3.gnarususercontent.com.br/4790-python/Resenhas_App_ChatGPT.txt")
    response.encoding = 'utf-8' # Manual override
    with open('reviews.txt', 'w', encoding='utf-8') as file:
        file.write(response.text)

def create_default_ai_client():
    return OpenAI(
        base_url = os.getenv("LLM_DEFAULT_BASE_URL"),
        api_key = os.getenv("LLM_DEFAULT_APIKEY")
    )


def read_text_file(path):
    text_list = []
    with open('./reviews.txt', 'r', encoding='utf=8') as file:
        for line in file:
            text_list.append(line)

    return text_list

def chat_with_ai(ai_client, model, prompt):
    completions = ai_client.chat.completions.create(
        model = model,
        messages = [
            {
                'role': 'system',
                'content': os.getenv("LLM_DEFAULT_SYSTEM")
            },
            {
                'role': 'user',
                'content': f'{prompt}' 
            },
        ],
        temperature=0.0,
    )

    return completions.choices[0].message.content


def classify_reviews(reviews):

    positive_reviews = []
    negative_reviews = []
    neutral_reviews = []
    undefined_reviews = []   

    for review in reviews:
        if (review.get('feeling')=='Positive'):
            positive_reviews.append(review.get('pt_br_review'))

        elif (review.get('feeling')=='Negative'):
            negative_reviews.append(review.get('pt_br_review'))

        elif (review.get('feeling')=='Neutral'):
            neutral_reviews.append(review.get('pt_br_review'))

        else:
            undefined_reviews.append(review.get('original_review'))

    return positive_reviews, negative_reviews, neutral_reviews, undefined_reviews

    

request_file_content();

model = os.getenv("LLM_DEFAULT_MODEL")

ai_client = create_default_ai_client()
reviews = read_text_file('./reviews.txt')
parsed_answers = []

for review in reviews:

    prompt = f"""
    Identify de lannguage andevaluate the content of the following review and parse as a json object with the following attributes:
    'user_id', 'user_name, 'original_review', 'pt_br_review', 'feeling'. 

    The feeling attribute MUST be one of the following: Positive, Negative, Neutral.
    The pt_br_review attribute must be the same as original_review, translated to Brazilian Portuguese
    The separator is the '$'

    Example of input: '00000001$Erinaldo$Great content'.
    Example of output:
        {{
            "user_id": "00000001",
            "user_name": "Erinaldo",
            "original_review": "Great content",
            "pt_br_review": "Excelente conteúdo",
            "feeling": "Positive"
        }},

    desricao:
    - ALL values are strings
    - The value before the first '$' must be applies to user_id
    - The value between the first and second '$' must be applied to user_name
    - The value after the second '$' must be applied original_review
    - the value set to original review must be translated and applied to pt_br_review
    - The value set to original_review MUST NOT HAVE the user_id neither the user_name in it
    - MAKE SURE the output is a valid json format

    here is the review: {review}
    """

    ai_answer = chat_with_ai(ai_client, model, prompt)
    parsed_answers.append(json.loads(ai_answer.replace('```json', '').replace('```', '')))

positive_reviews, negative_reviews, neutral_reviews, undefined_reviews = classify_reviews(parsed_answers)
joined_reviews = positive_reviews + negative_reviews + neutral_reviews + undefined_reviews

'#####'.join(joined_reviews)

print(f'Positive reviews: {len(positive_reviews)}')
print(f'Negative reviews: {len(negative_reviews)}')
print(f'Neutral reviews: {len(neutral_reviews)}')
print(f'Undefined reviews: {len(undefined_reviews)}')

print('*'*10)
print(f'Reviews: {joined_reviews}')