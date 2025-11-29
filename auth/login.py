import mechanicalsoup
from config.settings import LOGIN_URL
import os
import config.settings

# Define function to login. ADding several browsers 

def login(username,password):
    browser = mechanicalsoup.StatefulBrowser( 
        soup_config={"features": "lxml"},
        raise_on_404=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/124.0.0.0 Safari/537.36"
    )

    # open web
    browser.open(LOGIN_URL)

    # selectlogin form 

    browser.select_form('#loginform')
    browser["log"] = username
    browser["pwd"] = password
    response = browser.submit_selected()

    return browser



