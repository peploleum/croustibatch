echo "The application is starting: ${CROUSTIBATCH_NAME} with parameters: ${INSIGHT_HOST} ${INSIGHT_PORT}"
python3 main.py --config "conf/openalpr.conf" --runtime_data "runtime_data" samples/us-2.jpg
