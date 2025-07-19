import requests

API_KEY = "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"  # اگه API واقعی داری جایگزین کن

def extract_text_from_image(image_url):
    payload = {
        'apikey': "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",
        'url': image_url,
        'language': 'fas'
    }
    res = requests.post("https://api.ocr.space/parse/imageurl", data=payload)
    result = res.json()
    return result['ParsedResults'][0]['ParsedText']
