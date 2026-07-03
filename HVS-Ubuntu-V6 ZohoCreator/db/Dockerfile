FROM mysql:8.0

# Balena no permite bind mounts; horneamos los scripts de inicialización en la
# imagen. MySQL los ejecuta automáticamente la primera vez que el directorio de
# datos está vacío (igual que el bind mount ./db/init que sustituye).
COPY init/ /docker-entrypoint-initdb.d/
