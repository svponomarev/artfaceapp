# ArtFaceApp utils/https_support

This directory contains files for setting up https configuration for nginx server in artfaceapp container.

This web application uses [EFF's Certbot][1] with [Let's Encrypt][2] SSL certificates. 
Basic instruction is taken from [here][3].
1. Attach to running artfaceapp container:
```
docker exec -it artfaceapp_artfaceapp_1 /bin/bash
```
2. Install nano text editor:
```
apt-get install nano
```
3. Enable the Jessie backports repo:
Open sources.list:
```
nano /etc/apt/sources.list
```
Append following line:
```
deb http://ftp.debian.org/debian jessie-backports main
```
Update sources:
```
apt-get update
```
4. Install certbot:
```
apt-get install certbot -t jessie-backports
```
5. Make directory for snippets in Nginx:
```
mkdir /etc/nginx/snippets
```
6. Create letsencrypt.conf and ssl-params.conf in /etc/nginx/snippets and copy content for them from corresponding files in repository

7. Replace text in /etc/nginx/conf.d/nginx.conf with text in file nginx-default.conf from repository

8. Install SSL certificate with Certbot:
```
certbot certonly --webroot --agree-tos --email sv.v.ponomarev@gmail.com -w /app -d www.artfaceapp.ru -d artfaceapp.ru
```
9. Replace text in /etc/nginx/conf.d/nginx.conf with text in file nginx.conf from repository

10. Reload Nginx server:
```
/usr/sbin/nginx -s reload
```
11. Install cron:
```
apt-get install cron
```
12. Add crontab to renew SSL certificate for Let's Encrypt every two months:
```
crontab -e
```
Append
```
0 0 1 JAN,MAR,MAY,JUL,SEP,NOV * certbot renew
```
## Authors

* **Svyatoslav Ponomarev** - sv.v.ponomarev@gmail.com

[1]: https://certbot.eff.org/
[2]: https://letsencrypt.org/
[3]: https://certbot.eff.org/#debianjessie-nginx
