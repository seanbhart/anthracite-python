# Gandalf Notion Gathering Service

NOTE: Google App Engine must be running to access Firestore and
other Google Cloud features.

## AWS Lightsail
```
ssh ubuntu@54.160.8.248
git clone https://github.com/seanbhart/anthracite-python.git
cd anthracite-python/
```

## Ubuntu Setup
### Install Python
```
sudo apt update
sudo apt install software-properties-common
sudo apt install python
```
### Install pyenv
```
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc

exec "$SHELL"
pyenv install 3.8.6
pyenv global 3.8.6
```

### Install Chromedriver
```
sudo apt-get install chromium-chromedriver
sudo apt-get install python-selenium python3-selenium
```
Chromedriver should be at: `/usr/lib/chromium-browser/chromedriver`


## Run App
```
sudo docker exec [container] /root/.pyenv/shims/python /slate/wishlist/main.py -d
```


## OTHER SETTINGS
Set local Google Cloud credentials
```
export GOOGLE_APPLICATION_CREDENTIALS=./local/Anthracite-31f494cd2bdf.json
```

Upload to Google Cloud (if using GAE)
```
gcloud functions deploy list_created \
  --runtime python38 \
  --trigger-event providers/cloud.firestore/eventTypes/document.create \
  --trigger-resource "projects/slate-21/databases/(default)/documents/lists/{list_id}"
```

## cron jobs
Setup a cron job to regularly run the script
- List current cron jobs: `crontab -l`
- Edit cron jobs: `crontab -e`
- Run command every 10 mins: `*/10 * * * * <command>` eg: `*/10 * * * * /path/to/python /path/to/file/main.py > log.txt`
- Clear exited containers (will accumulate in storage otherwise): `docker rm -v $(docker ps -aq -f 'status=exited')`
- Insert, save, quit: `i`, `:w`, `:q`
- Check cron log: `cat /var/spool/mail/ec2-user`
- Check root cron log: `sudo cat /var/spool/mail/root`

## Linux
- Check space: `df -h`
- Check dir size: `sudo du -xhs /*`
- Check file sizes: `sudo du -x -h / | sort -h | tail -40`
- Check running services in dir: `sudo lsof +D /var`
- Stop docker service: `sudo service docker stop`
- Remove docker resources: `sudo rm -rf /var/lib/docker/`
- Restart docker: `sudo service docker start`
