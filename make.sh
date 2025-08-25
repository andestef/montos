cd montos
sudo python ../montos.py
cd ../
FILE=".montos.rebootf"
if [ -f "$FILE" ]; then
sudo rm "$FILE"
sudo sh make.sh
fi
FILE=".montos.shutdownf"
if [ -f "$FILE" ]; then
sudo rm "$FILE"
sudo shutdown now
fi