# Slate Amazon Wishlist Detail Requester

NOTE: Google App Engine must be running to access Firestore and
other Google Cloud features.

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