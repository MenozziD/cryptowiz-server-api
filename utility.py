from json import load, dumps, loads ,dump
from logging import info, exception
from urllib.request import urlopen, Request
from os import walk, path
import requests
from WorkPixil.src import gen_img
from copy import deepcopy

def make_request(url, body=None, pinata=None):
    info("MAKE REQUEST: %s", url)
    to_return = {}
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'
    }
    if pinata is not None:
        header['pinata_api_key'] = Config.settings['pinata']['api_key']
        header['pinata_secret_api_key'] = Config.settings['pinata']['secret']
        request = requests.Request(
            'POST', 
            url,
            headers=header,
            files=pinata
        ).prepare()
        response = requests.Session().send(request)
        info(response.request.body)
        to_return['response'] = response.json()
        info("RESPONSE: %s", to_return['response'])
        to_return['state'] = True
    else:
        if body is not None:
            header['Content-Type'] = 'application/json'
            req = Request(url, data=bytes(dumps(body), encoding="utf-8"), headers=header)
        else:
            req = Request(url, headers=header)
        try:
            to_return['response'] = urlopen(req).read().decode()
            if to_return['response'] is None and validate_format(to_return['response']):
                to_return['response'] = loads(to_return['response'])
            info("RESPONSE: %s", to_return['response'])
            to_return['state'] = True
        except Exception as e:
            exception(e)
            to_return['state'] = False
            to_return['response'] = f"Si è verificato un errore nella chiamata a {url}"
            to_return['error_detail'] = str(e)
    return to_return

def read_file(file_path, json=True):
    f = open(file_path)
    if json:
        ctx = load(f)
    else:
        ctx = f.read()
    f.close()
    return ctx


def write_file(file_path, ctx, json=True):
    f = open(file_path, 'w')
    if json:
        dump(ctx, f)
    else:
        f.write(ctx)
    f.close()
    return True


def validate_format(request_validate):
    try:
        loads(request_validate)
    except ValueError:
        return False
    return True

def be_generate_nft(source_file, template_file, destination, name, description):
    work_pixil_path = Config.settings['endpoint']['work_pixil']
    source = f"{work_pixil_path}source/{source_file}"
    template = f"{work_pixil_path}template/{template_file}"
    info(destination)
    metadata = deepcopy(Config.settings["template_metadata"])
    metadata["description"] = description
    metadata["name"] = name
    metadata["custom_data"] = gen_img(source, template, False, destination, f"{work_pixil_path}src/")["json"]
    traits = []
    for k, v in metadata["custom_data"]["total"].items():
        traits.append({
            "trait_type": k.title(),
            "display_type": None,
            "value": v,
            "max_value": 50
        })
    for i in metadata["custom_data"]["items"]:
        traits.append({
            "trait_type": i['display_type'].title(),
            "display_type": None,
            "value": i['value_type'].title()
        })
    metadata["attributes"] = traits
    '''
    metadata["custom_data"] = {}
    metadata.pop('custom_data', None)
    metadata.pop('traits', None)
    '''
    return metadata


def pinata_upload(directory):
    files = []
    files.append(('pinataMetadata', (None, '{"name":"' + directory.split("\\")[-1] + '"}')))
    for root, dirs, files_ in walk(path.abspath(directory)):        
        for f in files_:
            p = root + '/' + f  
            files.append(('file', ('/'.join(p.split("\\")[-1:]) , open(p, 'rb'))))
    return make_request("https://api.pinata.cloud/pinning/pinFileToIPFS", pinata=files)


class Config:

    settings = {}

    @staticmethod
    def reload():
        Config.settings = read_file("config.json")
