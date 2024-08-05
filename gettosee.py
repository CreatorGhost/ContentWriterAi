from langchain_anthropic import ChatAnthropic
import os
from langchain.prompts import PromptTemplate
import json
from wordpressget import post_html_to_wordpress
from langchain_google_genai import ChatGoogleGenerativeAI
from wordpress import WordPressClient
from langchain_openai import ChatOpenAI


# llm = ChatGoogleGenerativeAI(model='gemini-1.5-pro-exp-0801')
# llm = ChatOpenAI(model="gpt-4o-mini")
wp_client = WordPressClient(wp_url=os.getenv('WP_URL_Get'), wp_user=os.getenv('WP_USER_Get'), wp_password=os.getenv('WP_PASSWORD_Get'))


api_key = os.getenv("ANTHROPIC_API_KEY")
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0.8,

)
template = """
You are an expert film critic and SEO specialist with a talent for engaging writing and a dash of humor. Create a comprehensive, highly SEO-optimized movie review based on the example content provided. Follow these instructions:
Analyze the example review(s) for structure, tone, key SEO elements, main points of critique, target keywords, and film terminology.
Write a detailed, original movie review of approximately 800 - 1000 words on a similar or related film.

Include a compelling, keyword-rich title.
Maintain a balanced, insightful tone appropriate for in-depth film criticism.
Incorporate identified keywords naturally throughout the text.
Use film terminology accurately, but explain complex concepts for a general audience.
Ensure the content is 100% original and does not copy from the example(s).
Verify all information is accurate and up-to-date.
Adhere to SEO best practices without keyword stuffing.

Format the review in proper HTML with appropriate headings and subheadings and also end it with proper html ending.
Provide only the title and review content in your response, without any additional messages or outline.

Example review(s) for reference:
{context}
Generate the comprehensive, SEO-optimized movie review based on these instructions."""







custom_rag_prompt = PromptTemplate.from_template(template)




with open('scraped_data_movies.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)



rag_chain = (
        custom_rag_prompt
        | llm
    )



# post_id = generate_and_post_to_wordpress('ai_post.html')
# print(post_id)

import time
for post in range(20,30):
    ai_post = rag_chain.invoke(posts[post]["content"])
    
    content = ai_post.content
    content = content.replace('```html', '').replace('```', '')
    with open('ai_post.html', 'w', encoding='utf-8') as html_file:
        html_file.write(content)

    post_id = wp_client.post_html_to_wordpress(ai_post.content)
    if post_id is None:
        print("Failed to publish post. Breaking the loop.")
        break

    print("Posted for no : ", post)
    if post % 3 == 0 and post != 0:
        time.sleep(3)
