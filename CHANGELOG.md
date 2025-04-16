# CHANGELOG

## Create a new version

```sh
rm -rf dist/ build/
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
# create egg-info folder
python3 -m twine upload dist/* --verbose
# use __token__ auth
# enter token
```

## 2025-04-16

- Version 1.0.1
- Supporting BMP
- Supporting PPM
- Acropalypse

## 2024-03-20

- Create package
