def get_name_from_url(url):
    name = url.rsplit('/', 1)[-1]
    # URL ends with a slash
    if not name:
        name = url.rsplit('/', 1)[-2].rsplit('/', 1)[-1]
    else:
        # URL has a file ending 
        if "." in name:
            name = name.rsplit('.', 1)[-2]
    return name

def escape_url(url, profile):
    if profile in ["delete", "get", "patch", "post", "put"]:
        url = url.replace("http:","http-"+profile+":")
        url = url.replace("https:","https-"+profile+":")
    elif profile == "get-put":
        url = url.replace("http:","http-get:")
        url = url.replace("https:","https-get:")
    url = url.replace(":", "%3A")
    url = url.replace("/", "%2F")
    return url
