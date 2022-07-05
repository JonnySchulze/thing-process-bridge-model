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

def check_for_media_type(input):
    comp = input.rsplit('/')
    if len(comp) == 2:
        return comp[0] in ["application", "audio", "font", "image", "model", "text", "video", "message"]
    return False

def typecast_default(input):
    # Boolean
    if input in ["True", "true"]:
        return True
    elif input in ["False", "false"]:
        return False  
    # Integer
    try:
        return int(input)
    except ValueError:
        pass
    # Float
    try:
        return float(input)
    except ValueError:
        pass
    return input