# ArtFaceApp utils/https_support

This directory contains files for setting up https configuration for nginx server in artfaceapp container.

This web application uses [ACME Shell script][1] with [Let's Encrypt][2] SSL certificates. 
Basic instruction is taken from [here][3].
1. Attach to running artfaceapp container:
```
docker exec -it artfaceapp_artfaceapp_1 /bin/bash
```
2. Update sources:
```
apt-get update
```
3. Install nano text editor and cron:
```
apt-get install nano cron
```
4. Make directory for snippets in Nginx:
```
mkdir /etc/nginx/snippets
```
5. Create letsencrypt.conf and ssl-params.conf in /etc/nginx/snippets and copy content for them from corresponding files in repository

6. Replace text in /etc/nginx/conf.d/nginx.conf with text in file nginx-default.conf from repository  

7. Reload Nginx server:
```
/usr/sbin/nginx -s reload  
```
8. Download ACME shell script:
```
wget -O -  https://get.acme.sh | sh -s email=sv.v.ponomarev@gmail.com
```
9. Issue SSL certificate using ACME:
```
./acme.sh --issue -d www.artfaceapp.ru -d artfaceapp.ru -w /app --server letsencrypt
```
10. Make directory for SSL certificates for Nginx:
```
mkdir -p /etc/letsencrypt/live/www.artfaceapp.ru/
```
11. Install SSL certificates in new directory using ACME:
```
./acme.sh --install-cert -d www.artfaceapp.ru \
--cert-file /etc/letsencrypt/live/www.artfaceapp.ru/cert.pem \
--key-file /etc/letsencrypt/live/www.artfaceapp.ru/privkey.pem \
--fullchain-file /etc/letsencrypt/live/www.artfaceapp.ru/fullchain.pem \
--reloadcmd "service nginx force-reload"
```
Copy fullchain.pem to chain.pem or use this command:
```
./acme.sh --install-cert -d www.artfaceapp.ru --fullchain-file /etc/letsencrypt/live/www.artfaceapp.ru/chain.pem --reloadcmd "service nginx force-reload"
```
12. Replace text in /etc/nginx/conf.d/nginx.conf with text in file nginx.conf from repository

13. Reload Nginx server:
```
/usr/sbin/nginx -s reload
```
## Authors

* **Svyatoslav Ponomarev** - sv.v.ponomarev@gmail.com

[1]: https://github.com/acmesh-official/acme.sh
[2]: https://letsencrypt.org/
[3]: https://github.com/acmesh-official/acme.sh/wiki
