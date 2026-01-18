# setup

```bash
# create venv
python -m venv .venv

# Activate venv
# Windows
.venv/scripts/activate
# Mac
source .venv/bin/activate

# install requirements
pip install -r requirements.txt
```

# adding requirement

```bash
#install
pip install [requirement]

# update requirements
pip freeze >requirements.txt
```

# running server

```bash
fastapi dev main.py
```
