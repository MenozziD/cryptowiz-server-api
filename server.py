from logic import get_nft_detail, get_nft_ids, make_collection
from utility import Config, validate_format
from json import loads
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from logging import basicConfig, INFO, info

# http://127.0.0.1:5000/nft_ids?contract=0x2953399124F0cBB46d2CbACD8A89cF0599974963&wallet=0x49b363595ecDB335BEa64E4850472d9eF0609c99&chain=matic
# http://127.0.0.1:5000/nft_detail?contract=0x2953399124F0cBB46d2CbACD8A89cF0599974963&id=86878125432023963361188205560853538656658503492234669844754453276830568808449&chain=matic
# http://127.0.0.1:5000/nft_detail?contract=0x6a709b054deb0c4b201df12e982b3196fc1bbff1&id=0&chain=rinkeby

app = Flask(__name__)
CORS(app)


@app.route('/nft_up', methods=["POST"])
@cross_origin()
def nft_up():
    to_ret = {}
    make_collection(Config.settings['endpoint']['work_pixil_gen'], 'c_itm_070522', 5, "items.json")
    to_ret['state'] = True
    info(f"RESPONSE: {to_ret}")
    return to_ret


@app.route('/nft_ids', methods=["POST"])
@cross_origin()
def nft_ids():
    body = request.data.decode()
    info(body)
    ret = check_params_nft_ids(body)
    if ret['state']:
        ret = get_nft_ids(loads(body))
    info(f"RESPONSE: {ret}")
    return ret


def check_params_nft_ids(body):
    to_ret = {
        'state': False
    }
    if body != "" and validate_format(body):
        body = loads(body)
        if 'contract' in body and body['contract'] != "":
            if 'wallet' in body and body['wallet'] != "":
                if 'chain' in body and body['chain'] in Config.settings["chains"].keys():
                    to_ret['state'] = True
                else:
                    to_ret[
                        'response'] = f"The parameter chain is mandatory, possible values: {', '.join(list(Config.settings['chains'].keys()))}"
            else:
                to_ret['response'] = "The parameter wallet is mandatory"
        else:
            to_ret['response'] = "The parameter contract is mandatory"
    else:
        to_ret['response'] = "Body is null or is not JSON format"
    return to_ret


@app.route('/nft_detail', methods=["POST"])
@cross_origin()
def nft_detail():
    body = request.data.decode()
    info(body)
    ret = check_params_nft_detail(body)
    if ret['state']:
        ret = jsonify(get_nft_detail(loads(body)))
    info(f"RESPONSE: {ret}")
    return ret


def check_params_nft_detail(body):
    to_ret = {
        'state': False
    }
    if body != "" and validate_format(body):
        body = loads(body)
        if 'contract' in body and body['contract'] != "":
            if 'id' in body and body['id'] != "":
                if 'chain' in body and body['chain'] in Config.settings["chains"].keys():
                    to_ret['state'] = True
                else:
                    to_ret['response'] = f"The parameter chain is mandatory, possible values: {', '.join(list(Config.settings['chains'].keys()))}"
            else:
                to_ret['response'] = "The parameter id is mandatory"
        else:
            to_ret['response'] = "The parameter contract is mandatory"
    else:
        to_ret['response'] = "Body is null or is not JSON format"
    return to_ret


if __name__ == '__main__':
    Config().reload()
    basicConfig(
        filename=Config.settings['log']['path_file'],
        format=Config.settings['log']['format'],
        level=INFO)
    app.run()
