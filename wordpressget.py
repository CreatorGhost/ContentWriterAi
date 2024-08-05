from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

# WordPress credentials and URL
WP_URL = os.getenv('WP_URL_Get')
WP_USER = os.getenv('WP_USER_Get')
WP_PASSWORD = os.getenv('WP_PASSWORD_Get')

def test_xmlrpc_connection():
    """Test the XML-RPC connection and print diagnostic information."""
    print(f"Testing connection to {WP_URL}")
    
    session = requests.Session()  # Use a session to handle cookies

    # Test basic connectivity
    try:
        response = session.get(WP_URL)
        print(f"Basic connectivity - Status Code: {response.status_code}")
        print(f"Response Content: {response.text[:100]}...")  # Print first 100 characters
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {WP_URL}: {e}")
        return

    # Try a simple XML-RPC request
    xml_request = f"""
    <?xml version="1.0"?>
    <methodCall>
    <methodName>wp.getUsersBlogs</methodName>
    <params>
     <param><value>{WP_USER}</value></param>
     <param><value>{WP_PASSWORD}</value></param>
    </params>
    </methodCall>
    """

    headers = {'Content-Type': 'text/xml'}
    try:
        response = session.post(WP_URL, data=xml_request, headers=headers, auth=HTTPBasicAuth(WP_USER, WP_PASSWORD))
        print(f"XML-RPC Status Code: {response.status_code}")
        print(f"XML-RPC Response Content: {response.text[:100]}...")
        
        if response.status_code == 409:
            print("Conflict detected. Retrying...")
            response = session.post(WP_URL, data=xml_request, headers=headers, auth=HTTPBasicAuth(WP_USER, WP_PASSWORD))
            print(f"Retry XML-RPC Status Code: {response.status_code}")
            print(f"Retry XML-RPC Response Content: {response.text[:100]}...")
    except requests.exceptions.RequestException as e:
        print(f"Error making XML-RPC request: {e}")

def post_html_to_wordpress(html_content):
    """
    Function to post an HTML article to WordPress using the wordpress_xmlrpc library.
    
    :param html_content: HTML content of the WordPress post
    :return: Response from the WordPress API
    """
    # Extract title from HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find(['h1', 'title'])  # Look for <h1> or <title> tags
    title = title_tag.get_text() if title_tag else "Default Title"

    # Remove the title tag from the HTML content
    if title_tag:
        title_tag.extract()  # Use extract() instead of decompose()

    try:
        # Post to WordPress
        client = Client(WP_URL, WP_USER, WP_PASSWORD)
        post = WordPressPost()
        post.title = title
        post.content = str(soup)
        post.post_status = 'draft'
        post_id = client.call(NewPost(post))
        return post_id
    except Exception as e:
        print(f"Error posting to WordPress: {e}")
        # test_xmlrpc_connection()  # Run diagnostic test if posting fails
        
        return None

# Example usage
if __name__ == "__main__":
    test_xmlrpc_connection()  # Run diagnostic test before attempting to post
    
    # Uncomment the following lines to test posting
    # with open('generated_page.html', 'r', encoding='utf-8') as html_file:
    #     html_content = html_file.read()
    # post_id = post_html_to_wordpress(html_content)
    # if post_id:
    #     print(f"Post published with ID: {post_id}")
    # else:
    #     print("Failed to publish post")