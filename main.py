from langchain_anthropic import ChatAnthropic
import os
from langchain.prompts import PromptTemplate
import json
from wordpress import WordPressClient
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

wp_client = WordPressClient(wp_url=os.getenv('WP_URL'), wp_user=os.getenv('WP_USER'), wp_password=os.getenv('WP_PASSWORD'))



llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0.8,

)

template = """
You are an expert SEO content writer specializing in technical topics, with a knack for adding light-hearted humor to your writing. Create a high-quality, SEO-friendly blog post based on the example content provided. Follow these instructions:
Analyze the example blog(s) for structure, tone, key SEO elements, main topic, target keywords, and technical jargon.
Write a completely original blog post of approximately 300 - 500 words on the same or a similar topic.

Include a compelling title.
Maintain a professional, authoritative tone appropriate for technical content.
Incorporate identified keywords naturally throughout the text.
Use technical terms accurately, but explain complex concepts for a general audience.
Ensure the content is 100% original and does not copy from the example(s).
Verify all technical information is accurate and up-to-date.
Adhere to SEO best practices without keyword stuffing.


Format the post in proper HTML with proper heading and sub heading.
Provide only the title and blog post content in your response, without any additional messages or outline.

Example blog(s) for reference:
{context}
Generate the blog post based on these instructions.
"""

custom_rag_prompt = PromptTemplate.from_template(template)




with open('scraped_data_tech.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

post = posts[0]["content"]

rag_chain = (
        custom_rag_prompt
        | llm
    )

# print(f"WP_URL: {WP_URL}, WP_USER: {WP_USER}, WP_PASSWORD: {WP_PASSWORD}")
def generate_and_post_to_wordpress(html_file_name):
    with open(html_file_name, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    post_id = post_html_to_wordpress(html_content)
    return post_id



for post in range(0, 1):
    ai_post = rag_chain.invoke(posts[post]["content"])
    with open('ai_post_.html', 'w', encoding='utf-8') as html_file:
        html_file.write(ai_post.content)
    post_id = wp_client.post_html_to_wordpress(ai_post.content)
    if post_id is None:
        print("Failed to publish post. Exiting.")
        break
    print(f"Posted for no: {post}")
    print(f"Number of posts left: {1 - post - 1}")
