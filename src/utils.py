def escape_url(url, profile):
    if profile in ["delete", "get", "patch", "post", "put"]:
        url = url.replace("http:","http-"+profile+":")
        url = url.replace("https:","https-"+profile+":")
    url = url.replace(":", "%3A")
    url = url.replace("/", "%2F")
    return url

def check_for_media_type(input):
    comp = input.rsplit('/')
    if len(comp) == 2:
        return comp[0] in ["application", "audio", "font", "image", "model", "text", "video", "message", "multipart"]
    return False

def typecast(input):
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
    # String
    return input