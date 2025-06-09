
# Run
```bash
pyinstaller main.spec --clean
```
# Building PyInstaller Bootloader Manually

If you get errors about missing bootloaders or pointer size, follow these steps:


## 2. Clone PyInstaller repo

```bash
git clone https://github.com/pyinstaller/pyinstaller.git
cd pyinstaller/bootloader
```


## 3. Configure and build bootloader with pointer size

Run these commands based on your system architecture:

```bash
# For 64-bit systems:
python waf --target-arch=64bit all 
```


## 4. Install PyInstaller from local repo

```bash
cd ..
pip install .
```


## 5. Use PyInstaller as usual

```bash
pyinstaller main.spec
```

