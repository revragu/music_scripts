#!/usr/bin/env python3

import sys, http.client, re, time, requests, json

# basic http api request to server that returns json
def httpReq(address_root,address_sub,req):
    resp=requests.get(address_root + address_sub, req)
    if resp.status_code == 200:
        return(json.loads(resp.content),resp.status_code)
    return(False,resp.status_code)

# take an http address and create a dict from it with the protocol, domain, and path in separate keys.
# strip leading/trailing spaces, split at slashes
# if the address contains a protocol at the front eg https://, split at :// , assign the split[0] as the protocol, then delete the protocol and extra / entries from the split.
# otherwise assume https
# loop through the split, set first iteration as domain, then reconstitute path on subsequent iterations
# return as dict
def formatHttpAddress(input_address):
    protocol = ''
    path = ''
    domain = ''
    input_address=input_address.strip()
    split_address = input_address.split('/')
    if re.match(r'^.*:\/\/', input_address):
        pc = input_address.split('://')
        protocol = pc[0]
        del split_address[0:2]
        
    else:
        protocol="https"
    
    for idx, section in enumerate(split_address):
        if idx == 0:
            domain = section
        else:
            path = path + '/' + section

    # get http/https

    address = {
        "protocol": protocol,
        "domain": domain,
        "path": path
    }
    return address

# get http content, takes input address
def getHttpContent(input_address):
    import random
    # take the formatted address, reconstitute full address from dict (this ensures that a protocol is specified)
    # make an http or https connection depending on protocol, otherwise fail
    # request page content and return response and content
    def getHttp(formatted_address):
        retry=0
        while retry < 5:
            backoff=random.randrange(0,500)/1000
            time.sleep(backoff)
            full_address = formatted_address["protocol"] +'://' + formatted_address["domain"] + formatted_address["path"]
            try:
                if formatted_address["protocol"] == "http":
                    connection = http.client.HTTPConnection(formatted_address["domain"], timeout=2)
                elif formatted_address["protocol"] == "https":
                    connection = http.client.HTTPSConnection(formatted_address["domain"], timeout=2)
                else:
                    raise RuntimeError("bad protocol: " + formatted_address["protocol"])
                connection.request('GET', formatted_address["path"])
                response = connection.getresponse()
                content = response.read().decode('utf-8', errors='ignore')
                return(response, content)
            except Exception as e:
                err=e
                time.sleep(5)
                retry+=1

    
        if err.args[0] == -2 and err.args[1] == 'Name or service not known':
            raise ConnectionError("Not able to connect to site, domain: " + formatted_address["domain"] + " path: " +  formatted_address["path"])
        elif err.args[0] == '[Errno -3] Temporary failure in name resolution':
            raise ConnectionError("Not able to connect to DNS")
        else:
            raise(err)
            
            


    # format http address into dict
    formatted_address = formatHttpAddress(input_address)
    # get content from http address, takes http address dict
    try:
        response, content = getHttp(formatted_address)
    except Exception as e:
        raise(e)
    
    # return address, response, and content requested
    http_content = {
        "address":  formatted_address,
        "response": response,
        "content": content    
    }
    
    
    return http_content

def main():
    pass


if __name__ == "__main__":
    main(sys.argv[1:])