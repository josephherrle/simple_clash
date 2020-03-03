python3 event.py
for i in {1..10}
do
	echo "Creating user, iteration $i"
	python3 client.py
done
python3 analytics.py