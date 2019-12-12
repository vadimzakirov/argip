echo 'starting'
screen -S PPARSER -dmS  python main.py > log.txt
echo 'started'
screen -ls
