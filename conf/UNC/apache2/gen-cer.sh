#!/bin/bash
 
#1)Make sure Apache has SSL enabled.
#2)Generate a certificate signing request (CSR).
#3)Generate a self-signed certificate.
#4)Copy the certificate and keys we've generated.
#5)Tell Apache about the certificate.
#6)Modify the VirtualHosts to use the certificate.
#7)Restart Apache and test.

#Source https://www.jamescoyle.net/how-to/1073-bash-script-to-create-an-ssl-certificate-key-and-request-csr/comment-page-1#comment-226977
#Make sure your script has execute permissions.
#chmod +x gen-cer
#You can then call the script with ./gen-cer and specify your domain name as an argument. For example:
#./gen-cer mynewwebserver.jamescoyle.net

echo "---------------------------"
echo "----Enabling SSL Module----"
echo "---------------------------"
sudo a2enmod ssl

domain=$1
commonname=$domain
 
#Change to your company details
country=AR
state=Cordoba
locality=Cordoba
organization='Grupo BinBash (BinBash, S.A.)'
organizationalunit='Grupo BinBash'
email=administrator@binbash.com.ar
 
#Optional
password=12345
 
if [ -z "$domain" ]
then
    echo "Argument not present."
    echo "Useage $0 [common name]"
 
    exit 99
fi
 
echo "Generating key request for $domain"
 
#Generating Private Key
#sudo openssl genrsa -des3 -passout pass:12345 -out server_private.key 1024
#openssl rsa -in server_private.key -passin pass:12345 -out server_private.key 

#Generate a key
openssl genrsa -des3 -passout pass:$password -out $domain.key 2048 -noout
 
#Remove passphrase from the key. Comment the line out to keep the passphrase
echo "Removing passphrase from key"
openssl rsa -in $domain.key -passin pass:$password -out $domain.key
 
#Create the request
echo "Creating CSR"
openssl req -new -key $domain.key -out $domain.csr -passin pass:$password \
    -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
 
echo "---------------------------"
echo "-----Below is your CSR-----"
echo "---------------------------"
echo
cat $domain.csr
 
echo
echo "---------------------------"
echo "-----Below is your Key-----"
echo "---------------------------"
echo
cat $domain.key

#Generating the certificate
openssl x509 -req -days 365 -in $domain.csr -signkey $domain.key -out $domain.crt

sudo cp $domain.crt /etc/ssl/certs/$domain.crt
sudo cp $domain.key /etc/ssl/private/$domain.key