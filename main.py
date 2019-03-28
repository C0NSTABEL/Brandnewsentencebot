import praw
import requests
import bs4
from urllib.parse import quote_plus
import re

reddit = praw.Reddit(
    client_id='CLIENT_ID',
    client_secret='SECRET',
    username='brandnewsentencebot',
    password='PASSWORD',
    user_agent='AGENT')
    
subreddit = reddit.subreddit("testingground4bots")
keyphrase = "r/brandnewsentence"
reply_template = "Actually, this phrase already exists in {}. ^((not counting special characters and numbers\\))\n\n\n[About the Library of Babel](https://libraryofbabel.info/About.html) \n\n^(I'm a bot, beep boop. Contact my creator u/C0NSTABEL to share your ideas, complaints or love for me :\\))"
blacklist = ["sneakpeekbot", "allegedlybot"]
URL = "https://libraryofbabel.info/search.cgi"

def onclick_to_url(text):
    ONCLICK_RE = r"postform\('(.*?)','(.*?)','(.*?)','(.*?)','(.*?)'(,'.*')*\)"
    match = re.fullmatch(ONCLICK_RE, text)
 
    hex_ = match.group(1)
    wall = match.group(2)
    shelf = match.group(3)
    volume = match.group(4)
    page = match.group(5)
 
    param = f"{hex_}-w{wall}-s{shelf}-v{volume}:{page}"
    url = f"https://libraryofbabel.info/book.cgi?{param}"
    return url

def search(text):
    response = requests.post(URL, data={"find": text, "method": "x"})
    soup = bs4.BeautifulSoup(response.content, "html.parser")
 
    exact_info = soup.find(string="exact match:").find_next("a")["onclick"]
    exact_url = onclick_to_url(exact_info)
    return str(exact_url)

def main():
    for comment in subreddit.stream.comments():
        if keyphrase not in comment.body.lower():
            continue
        parent = comment.parent()
        if type(parent) != praw.models.reddit.comment.Comment or str(comment.author.name).lower() in blacklist:
            continue
        alreadyReplied = False
        comment.refresh()
        comment.reply_limit = 15
        for replies in comment.replies:
            if comment.replies:
                if str(replies.author).lower() == "brandnewsentencebot":
                    alreadyReplied = True
        if alreadyReplied:
            continue
        if len(parent.body) > 3199:
        	continue
        print("replying to: {}".format(comment.author))
        print("reddit.com{}".format(comment.permalink))
        query = parent.body
        library_of_babel_url = search(query)
        library_of_babel_rlink = f"[The Library Of Babel]({library_of_babel_url})"
        full_reply = reply_template.format(library_of_babel_rlink)
        comment.reply(full_reply)

if __name__ == "__main__":
	main()
