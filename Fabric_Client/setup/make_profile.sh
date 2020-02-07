#!/bin/bash          

NETWORK=$1
VERSION=$2

ORG1_CERT=$(awk 'NF {sub(/\r/, ""); printf "%s\\\\n",$0;}' ../../network/crypto-config/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt )
ORG2_CERT=$(awk 'NF {sub(/\r/, ""); printf "%s\\\\n",$0;}' ../../network/crypto-config/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt )
ORDERER0_CERT=$(awk 'NF {sub(/\r/, ""); printf "%s\\\\n",$0;}' ../../network/crypto-config/ordererOrganizations/example.com/orderers/orderer0.example.com/tls/ca.crt )
ORDERER1_CERT=$(awk 'NF {sub(/\r/, ""); printf "%s\\\\n",$0;}' ../../network/crypto-config/ordererOrganizations/example.com/orderers/orderer1.example.com/tls/ca.crt )


cp -r ./template/network.json ./

sed -i "s~INSERT_ORG1_CA_CERT~$ORG1_CERT~g" ./network.json
sed -i "s~INSERT_ORG2_CA_CERT~$ORG2_CERT~g" ./network.json
sed -i "s~INSERT_ORDERER0_CA_CERT~$ORDERER0_CERT~g" ./network.json
sed -i "s~INSERT_ORDERER1_CA_CERT~$ORDERER1_CERT~g" ./network.json
