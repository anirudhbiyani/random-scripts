import json
import requests
import os
import sys
import subprocess
import logging
from collections import defaultdict
from slacker import Slacker

TOKEN = os.getenv("TOKEN")
UNAME = os.getenv("UNAME")
UPASS = os.getenv("UPASS")


def get_current_image():
    params = (("page_size", "10000"),)
    data = {"username": UNAME, "password": UPASS}
    response = requests.post("https://hub.docker.com/v2/users/login/", data=data)
    token1 = response.text
    customer = json.loads(token1)
    TOKEN = customer["token"]
    open(
        "/tmp/docker_image.txt", "w"
    ).close()
    headers = {
        "Authorization": "JWT " + TOKEN,
    }
    response = requests.get(
        "https://hub.docker.com/v2/repositories/credsre/",
        headers=headers,
        params=params,
    )
    res = response.json()
    print(res)
    results = res["results"]
    for result in results:
        if result["is_private"]:
            keyword_f = open(
                "/tmp/docker_image.txt",
                "a",
            )
            keyword_f.write("credsre/" + result["name"] + "\n")
            keyword_f.close()


def compare_hash(foundimage, dockerhublist):
    """
    This function will compare the hashes and will returns dict.
    dockerhubList: cred images from docker hub.
    foundimage: found image on dockerhub.
    """
    exposed_images = []
    command = [
        "skopeo",
        "--override-os=linux",
        "inspect",
        "docker://docker.io/" + str(dockerhublist),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err.decode() != "":
        logging.error(err.decode())
    json_output = json.loads(out.decode())
    hash_to_check1 = json_output["Digest"].split(":")[1]
    command = [
        "skopeo",
        "--override-os=linux",
        "inspect",
        "docker://docker.io/" + str(foundimage),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err.decode() != "":
        command = [
            "skopeo",
            "--override-os=linux",
            "inspect",
            "docker://docker.io/" + str(foundimage) + ":master",
        ]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err1 = process.communicate()
        if err1.decode() != "":
            logging.error(err.decode())
    json_output = json.loads(out.decode())
    hash_to_check2 = json_output["Digest"].split(":")[1]
    if hash_to_check1 == hash_to_check2:
        print("Exposed Image found: ", foundimage)
        exposed_images.append(foundimage)
    SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
    slack = Slacker(SLACK_API_TOKEN)
    slackChannel = os.getenv("SLACK_CHANNEL")
    slack.chat.post_message(
        channel=slackChannel,
        text="Please review the list of public docker images: "
        + foundimage
        + "-->"
        + dockerhublist,
    )


def search_dockerhub(keywords_to_search):
    """
    This function will take list of keywords and search them in dockerhub.
    keywords_to_search: The list of keywords to search.
    """
    dockerhub = []  # registries found
    keywords = keywords_to_search.split("\n")
    print(keywords)

    for keyword in keywords:
        image_name = keyword.split("/")
        if keyword == "":
            continue
        url = "https://hub.docker.com/api/content/v1/products/search?page_size=100&q={0}&type=image".format(
            image_name[-1]
        )
        print(url)
        try:
            res_dockerhub = requests.get(url, headers={"Search-Version": "v3"})
        except Exception as e:
            logging.error(e)
            continue
        res_dockerhub_dict = json.loads(res_dockerhub.text)
        print_count, page_count = 0, 1
        total_count = res_dockerhub_dict["count"]
        if res_dockerhub_dict["count"] > 0:
            summary_list = res_dockerhub_dict["summaries"]
            for item in summary_list:
                dockerhub.append(item["name"])
                print_count += 1
        while print_count < total_count:
            page_count += 1
            url = "https://hub.docker.com/api/content/v1/products/search?page_size=100&q={0}&type=image&page={1}".format(
                image_name[-1], page_count
            )
            print(url)
            try:
                res_dockerhub = requests.get(url, headers={"Search-Version": "v3"})
                res_dockerhub_dict = json.loads(res_dockerhub.text)
                if (
                    res_dockerhub.status_code != 200
                    or res_dockerhub_dict["summaries"] is None
                ):
                    break
                summary_list = res_dockerhub_dict["summaries"]
                for item in summary_list:
                    dockerhub.append(item["name"])
                    print(item["name"], "-->", image_name[-1])
                    print(keyword)
                    compare_hash(item["name"], keyword)
                    print_count += 1
            except Exception as e:
                logging.error(e)
                break
    return dockerhub


def main():
    keyword_f = open(
        "/tmp/docker_image_keywords_to_search.txt",
        "r",
    )
    local_keywords = keyword_f.read()
    print(local_keywords)
    keyword_f.close()
    public_images = []
    # Searching in dockerhub
    logging.info("Searching for public image based on keywords")
    public_images = search_dockerhub(local_keywords)
    print(public_images)
    get_current_image()
    keyword_f1 = open(
        "/tmp/docker_image.txt"
    )
    local_keywords1 = keyword_f1.read()
    print(local_keywords1)
    public_images1 = search_dockerhub(local_keywords1)
    print(public_images1)


if __name__ == "__main__":
    main()
