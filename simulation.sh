python3 event.py
for i in {1..10}
do
	python3 client.py &
done
python3 analytics.py