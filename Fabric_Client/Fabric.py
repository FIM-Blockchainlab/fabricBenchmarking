#  Copyright 2019  ChainLab
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import os
import subprocess

from BlockchainFormation import vm_handler

from BlockchainFormation.utils.utils import wait_till_done


def fabric_client_startup(fabric_config, client_config, logger):
    """
    Copies the needed files to the clients, install all needed packages and runs a test to verfiy the success
    :param fabric_config:
    :param client_config:
    :param logger:
    :return:
    """
    # TODO add more comments

    dir_name = os.path.dirname(os.path.realpath(__file__))
    src_name = os.path.realpath(os.path.dirname(os.path.dirname(dir_name)))

    logger.info("Setting up the clients with the fabric-specific files")

    logger.debug("Creating directories for raw and evaluation data")
    os.system(f"mkdir {client_config['exp_dir']}/benchmarking")

    logger.debug("Copying static client setup stuff and benchmarking.js")
    os.system(f"cp -r {dir_name}/setup {client_config['exp_dir']}")
    os.system(f"mkdir {client_config['exp_dir']}/network")
    os.system(f"cp {src_name}/benchmarking/benchmarking.js {client_config['exp_dir']}/setup")

    logger.debug("Copying User-specific credentials")
    os.system(f"mkdir {client_config['exp_dir']}/setup/creds")

    logger.debug("Writing replacement script")
    write_replacement(fabric_config, client_config)

    for org in range(1, fabric_config['fabric_settings']['org_count'] + 1):
        os.system(f"cp -r {fabric_config['exp_dir']}/setup/crypto-config/peerOrganizations/org{org}.example.com/users/User1@org{org}.example.com {client_config['exp_dir']}/setup/creds")

    logger.debug("Finalizing setup stuff for every client and push it to the clients")
    ssh_clients, scp_clients = vm_handler.VMHandler.create_ssh_scp_clients(client_config)
    for client, _ in enumerate(ssh_clients):
        client_installation(fabric_config, client_config, ssh_clients, scp_clients, client, logger)

    logger.debug("Waiting until all installations have been completed")
    status_flags = wait_till_done(fabric_config, ssh_clients, client_config['ips'], 300, 10, "/home/ubuntu/setup/deploy.log", "done", 180, logger)

    if False in status_flags:
        raise Exception("Installation failed")

    logger.info("Installation and wallet creation were successful")
    logger.info("                                 ")
    logger.info("=================================")
    logger.info("      Client setup completed     ")
    logger.info("=================================")
    logger.info("                                 ")
    logger.info("Conducting a small test")
    stdin, stdout, stderr = ssh_clients[0].exec_command("(cd /home/ubuntu/setup && . ~/.profile && node test.js)")
    logger.debug("".join(stdout.readlines()))
    logger.debug("".join(stderr.readlines()))
    logger.debug("Test finished")


def write_network(fabric_config, client_config, client):
    """

    :param fabric_config:
    :param client_config:
    :param client:
    :return:
    """

    if fabric_config['fabric_settings']['tls_enabled'] == 1:
        http_string = "https"
        grpc_string = "grpcs"
    else:
        http_string = "http"
        grpc_string = "grpc"

    with open(f"{client_config['exp_dir']}/setup/network.json", "w+") as file:

        network = {}
        network["name"] = "my-net"
        network["x-type"] = "hlfv1"
        network["x-commitTimeout"] = 60
        network["version"] = "1.0.0"
        network["channels"] = {
            "mychannel": {
                "orderers": [],
                "peers": {}
            }
        }
        network["organizations"] = {}
        network["orderers"] = {}
        network["peers"] = {}
        network["certificateAuthorities"] = {}

        for org in range(0, fabric_config['fabric_settings']['org_count']):
            org = org + 1

            network["organizations"][f"Org{org}"] = {
                "mspid": f"Org{org}MSP",
                "peers": [],
                "certificateAuthorities": [
                    f"ca_org{org}"
                ]
            }

            """
            network["certificateAuthorities"][f"ca_org{org}"] = {
                "url": f"{http_string}://{ip}:7054",
                "name": f"ca_org{org}",
                "httpOptions": {
                    "verify": False
                }
            }
            """

            for peer in range(0, fabric_config['fabric_settings']['peer_count']):
                index_peer = fabric_config['peer_indices'][(org-1) * fabric_config['fabric_settings']['peer_count'] + peer]
                ip_peer = fabric_config['priv_ips'][index_peer]
                if (fabric_config['fabric_settings']['endorsement_policy'].upper() == "OR"):
                    if (client%(fabric_config['fabric_settings']['org_count']) + 1 == org and ((client-(org-1))/fabric_config['fabric_settings']['org_count'])%(fabric_config['fabric_settings']['peer_count']) == peer):
                        network["channels"]["mychannel"]["peers"][f"peer{peer}.org{org}.example.com"] = {
                            "endorsingPeer": True,
                            "chaincodeQuery": True,
                            "eventSource": True
                        }
                    else:
                        pass
                        # network["channels"]["mychannel"]["peers"][f"peer{peer}.org{org}.example.com"] = {
                            # "endorsingPeer": False,
                            # "chaincodeQuery": False,
                            # "eventSource": False
                        # }
                elif (fabric_config['fabric_settings']['endorsement_policy'].upper() == "AND"):
                    if (client%(fabric_config['fabric_settings']['peer_count']) == peer):
                        network["channels"]["mychannel"]["peers"][f"peer{peer}.org{org}.example.com"] = {
                            "endorsingPeer": True,
                            "chaincodeQuery": True,
                            "eventSource": True
                        }
                    else:
                        pass
                        # network["channels"]["mychannel"]["peers"][f"peer{peer}.org{org}.example.com"] = {
                            # "endorsingPeer": False,
                            # "chaincodeQuery": False,
                            # "eventSource": False
                        # }

                network["organizations"][f"Org{org}"]["peers"].append(f"peer{peer}.org{org}.example.com")

                if fabric_config['fabric_settings']['tls_enabled'] == 1:
                    url_string = f"{grpc_string}://peer{peer}.org{org}.example.com:7051"
                else:
                    url_string = f"{grpc_string}://{ip_peer}:7051"

                network["peers"][f"peer{peer}.org{org}.example.com"] = {
                    "url": url_string,
                    "grpcOptions": {
                        "ssl-target-override": f"peer{peer}.org{org}.example.com"
                    },
                    "tlsCACerts": {
                        "pem": f"INSERT_ORG{org}_CA_CERT"
                    }
                }

        for orderer, index_orderer in enumerate(fabric_config['orderer_indices']):
            orderer = orderer + 1

            ip_orderer = fabric_config['priv_ips'][index_orderer]

            network["channels"]["mychannel"]["orderers"].append(f"orderer{orderer}.example.com")

            network["orderers"][f"orderer{orderer}.example.com"] = {
                "url": f"{grpc_string}://{ip_orderer}:7050",
                "grpcOptions": {
                    "ssl-target-name-override": f"orderer{orderer}.example.com"
                },
                "tlsCACerts": {
                    "pem": f"INSERT_ORDERER{orderer}_CA_CERT"
                }
            }

        json.dump(network, file, indent=4)


def write_replacement(fabric_config, client_config):
    """
    TODO
    :param fabric_config:
    :param client_config:
    :return:
    """

    with open(f"{client_config['exp_dir']}/setup/replacement.sh", "w+") as f:

        f.write("#!/bin/bash\n\n")
        f.write("NETWORK=$1\nVERSION=$2\n\n")

        for peer_org in range(1, fabric_config['fabric_settings']['org_count'] + 1):
            f.write(f"ORG{peer_org}" + """_CERT=$(awk 'NF {sub(/\\r/, ""); printf "%s\\\\\\\\n",$0;}'""" + f" {fabric_config['exp_dir']}/setup/crypto-config/peerOrganizations/org{peer_org}.example.com/peers/peer0.org{peer_org}.example.com/tls/ca.crt )\n")

        for orderer in range(1, fabric_config['fabric_settings']['orderer_count'] + 1):
            f.write(f"ORDERER_CERT{orderer}" + """=$(awk 'NF {sub(/\\r/, ""); printf "%s\\\\\\\\n",$0;}'""" + f" {fabric_config['exp_dir']}/setup/crypto-config/ordererOrganizations/example.com/orderers/orderer{orderer}.example.com/tls/ca.crt )\n")
            f.write("\n")

        f.write("\n\n\n")

        for peer_org in range(1, fabric_config['fabric_settings']['org_count'] + 1):
            f.write(f'sed -i "s~INSERT_ORG{peer_org}_CA_CERT~$ORG{peer_org}_CERT~g"' + f" {client_config['exp_dir']}/setup/network.json\n")

        for orderer in range(1, fabric_config['fabric_settings']['orderer_count'] + 1):
            f.write(f'sed -i "s~INSERT_ORDERER{orderer}_CA_CERT~$ORDERER_CERT{orderer}~g"' + f" {client_config['exp_dir']}/setup/network.json\n")

        f.close()


def write_config(client_config, org, sk_name):
    """

    :param client_config:
    :param org:
    :param sk_name:
    :return:
    """

    with open(f"{client_config['exp_dir']}/setup/config.json", "w+") as file:

        config = {}
        config["gateway"] = "./network.json"
        config["userName"] = f"User1@org{org}.example.com"
        config["MSPName"] = f"Org{org}MSP"
        config["keyName"] = sk_name

        json.dump(config, file, indent=4)


def client_installation(fabric_config, client_config, ssh_clients, scp_clients, client, logger):
    """
    Install all needed dependencies and files and the clients
    :param fabric_config:
    :param client_config:
    :param ssh_clients:
    :param scp_clients:
    :param client:
    :param logger:
    :return:
    """

    # logger.debug("Writing network.json for client{client}")
    write_network(fabric_config, client_config, client)

    org = (client % (fabric_config['fabric_settings']['org_count'])) + 1
    sk_name = subprocess.Popen(f"ls {client_config['exp_dir']}/setup/creds/User1@org{org}.example.com/msp/keystore/", shell=True, stdout=subprocess.PIPE).stdout.readlines()[0].decode("utf8").replace("\n", "")
    write_config(client_config, org, sk_name)

    # logger.debug("Finalizing network.json")
    os.system(f"bash {client_config['exp_dir']}/setup/replacement.sh")
    scp_clients[client].put(f"{client_config['exp_dir']}/setup", "/home/ubuntu", recursive=True)
    os.system(f"mv {client_config['exp_dir']}/setup/network.json {client_config['exp_dir']}/network/network_client{client}.json")

    channel = ssh_clients[client].get_transport().open_session()
    channel.exec_command("(cd /home/ubuntu/setup && . ~/.profile && npm install >> install.log && node addToWallet.js >> deploy.log)")

    # For debug mode on node SDK
    # logger.info("Starting SDK Client in debug mode")
    # stdin, stdout, stderr = ssh_clients[client].exec_command("export HFC_LOGGING='{\"debug\":\"console\",\"info\":\"console\"}'")
    # export HFC_LOGGING='{"debug":"console","info":"console"}'
    # logger.debug(stdout.readlines())
    # logger.debug(stderr.readlines())
    # performing benchmarking test

    # Adapting hosts because override does not seem to work
    if fabric_config['fabric_settings']['tls_enabled'] == 1:
        stdin, stdout, stderr = ssh_clients[client].exec_command("touch ~/hostadd")
        stdout.readlines()
        # logger.debug(stdout.readlines())
        # logger.debug(stderr.readlines())
        for org in range(1, fabric_config['fabric_settings']['org_count'] + 1):
            for peer in range(0, fabric_config['fabric_settings']['peer_count']):
                index_peer = fabric_config['peer_indices'][(org - 1) * fabric_config['fabric_settings']['peer_count'] + peer]
                ip_peer = fabric_config['priv_ips'][index_peer]
                stdin, stdout, stderr = ssh_clients[client].exec_command(f"echo {ip_peer} peer{peer}.org{org}.example.com >> ~/hostadd")
                stdout.readlines()
                # logger.debug(stdout.readlines())
               # logger.debug(stderr.readlines())

        stdin, stdout, stderr = ssh_clients[client].exec_command("sudo echo $(cat /etc/hosts) >> ~/hostadd")
        stdout.readlines()
        # logger.debug(stdout.readlines())
        # logger.debug(stderr.readlines())
        stdin, stdout, stderr = ssh_clients[client].exec_command("sudo mv ~/hostadd /etc/hosts")
        stdout.readlines()
        # logger.debug(stdout.readlines())
        # logger.debug(stderr.readlines())