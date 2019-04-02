import praw
import requests
import bs4
import re

reddit = praw.Reddit(
		client_id='',

		client_secret='',

		username='brandnewsentencebot',

		password='',

		user_agent='brandnewsentencebot by u/C0NSTABEL') #what even is this?

subreddit = reddit.subreddit("all")
keyphrase = "r/brandnewsentence"
reply_template = "Actually, this phrase already exists in {}. \n\n^((no special characters or numbers\\))\n\n\n^(I'm a bot, beep boop. To discuss me, contact my creator u/C0NSTABEL :\\))"
blacklist = ["sneakpeekbot", "allegedlybot", "brandnewsentencebot"]
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
	fail_counter = 0
	for comment in subreddit.stream.comments():
		if keyphrase not in comment.body.lower() or comment.subreddit == "BrandNewSentence": #this should prevent it from showing up in that subreddit right?
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
		library_of_babel_rlink = f"[here in The Library Of Babel]({library_of_babel_url})"
		full_reply = reply_template.format(library_of_babel_rlink)
		try:
			comment.reply(full_reply)
			reddit.redditor("C0NSTABEL").message("results!","reddit.com{}".format(comment.permalink))
		except praw.exceptions.APIException:	#If the comment limit is reached it just skips that comment
			fail_counter += 1
			print("failure ({} times)".format(str(fail_counter)))
			if fail_counter == 50:
				reddit.redditor("C0NSTABEL").message("Bot stopped","bot is no longer running")
				break

if __name__ == "__main__":
	main()
