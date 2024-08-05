

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

class WordPressClient:
    def __init__(self, wp_url=None, wp_user=None, wp_password=None):
        self.wp_url = wp_url or os.getenv('WP_URL')
        self.wp_user = wp_user or os.getenv('WP_USER')
        self.wp_password = wp_password or os.getenv('WP_PASSWORD')
        self.session = requests.Session()  # Use a session to handle cookies
    def test_xmlrpc_connection(self):
        """Test the XML-RPC connection and print diagnostic information."""
        print(f"Testing connection to {self.wp_url}")

        # Test basic connectivity
        try:
            response = self.session.get(self.wp_url)
            print(f"Basic connectivity - Status Code: {response.status_code}")
            print(f"Response Content: {response.text[:100]}...")  # Print first 100 characters
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {self.wp_url}: {e}")
            return

        # Try a simple XML-RPC request
        xml_request = f"""
        <?xml version="1.0"?>
        <methodCall>
        <methodName>wp.getUsersBlogs</methodName>
        <params>
         <param><value>{self.wp_user}</value></param>
         <param><value>{self.wp_password}</value></param>
        </params>
        </methodCall>
        """

        headers = {'Content-Type': 'text/xml'}
        try:
            response = self.session.post(self.wp_url, data=xml_request, headers=headers, auth=HTTPBasicAuth(self.wp_user, self.wp_password))
            print(f"XML-RPC Status Code: {response.status_code}")
            print(f"XML-RPC Response Content: {response.text[:100]}...")

            if response.status_code == 409:
                print("Conflict detected. Retrying...")
                response = self.session.post(self.wp_url, data=xml_request, headers=headers, auth=HTTPBasicAuth(self.wp_user, self.wp_password))
                print(f"Retry XML-RPC Status Code: {response.status_code}")
                print(f"Retry XML-RPC Response Content: {response.text[:100]}...")
        except requests.exceptions.RequestException as e:
            print(f"Error making XML-RPC request: {e}")

    def post_html_to_wordpress(self, html_content):
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
            client = Client(self.wp_url, self.wp_user, self.wp_password)
            post = WordPressPost()
            post.title = title
            post.content = str(soup)
            post.post_status = 'draft'
            post_id = client.call(NewPost(post))
            return post_id
        except Exception as e:
            print(f"Error posting to WordPress: {e}")
            # self.test_xmlrpc_connection()  # Run diagnostic test if posting fails

            return None

# Example usage
if __name__ == "__main__":
    wp_client = WordPressClient()
    wp_client.test_xmlrpc_connection()  # Run diagnostic test before attempting to post
