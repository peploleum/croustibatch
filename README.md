# croustibatch
Python batch processing


## Development: Windows 10

        unzip docker/raw/w64.7z
        cd [...]/openalpr-2.3.0/src/bindings/python
        python setup.py install --record files.txt
        
openalpr python libs should now be installed

        main.py --config "conf/openalpr.conf" --runtime_data "runtime_data" samples/us-2.jpg

## build as Docker container

        call build.bat
        cd docker/
        docker-compose -f croustibatch.yml up