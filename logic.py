from utility import make_request, Config, be_generate_nft, pinata_upload, write_file
from logging import exception, info
from os import mkdir, path
from shutil import rmtree


def get_nft_detail(payload):
    return make_request(Config.settings["chains"][payload["chain"]]["nft_detail_url"].replace("[contract]", payload["contract"]).replace("[id]", payload["id"]))


def get_nft_ids(payload):
    res = make_request(Config.settings["chains"][payload["chain"]]['nft_id_url'].replace("[contract]", payload["contract"]).replace("[wallet]", payload["wallet"]))
    if res['state']:
        try:
            token_ids = []
            for o in str(res['response']).split("tbody")[1].split("?a="):
                if o.split("target=")[0][0] != ">":
                    token_ids.append(o.split("target=")[0][:-2])
            res['response'] = {"token_ids": token_ids}
        except Exception as e:
            exception(e)
            res['response'] = str(e)
    return res


def make_collection(path_dir, name, size, template_workpixil):
    final_dir = path_dir + name
    metadata_list = []
    mkdir(final_dir + "_img")
    mkdir(final_dir + "_meta")
    for i in range(size):
        metadata_list.append(be_generate_nft("finale.pixil", template_workpixil, f"{final_dir}_img/{str(i)}.png", f"CryptoWiz - {str(i)}", f"The CryptoWiz number {str(i)}"))
    resp = pinata_upload(path.abspath(final_dir + '_img'))["response"]
    for i in range(size):
        metadata_list[i]['image'] = metadata_list[i]['image'].replace("{path_img}", f"{resp['IpfsHash']}/{str(i)}.png")
        write_file(f"{final_dir}_meta/{str(i)}.json", metadata_list[i])
    pinata_upload(path.abspath(final_dir + '_meta'))
    rmtree(final_dir + "_img")
    rmtree(final_dir + "_meta")
