# croustibatch
Python batch processing


## Development: Windows 10

        unzip docker/raw/w64.7z
        cd [...]/openalpr-2.3.0/src/bindings/python
        python setup.py install --record files.txt
        
openalpr python libs should now be installed

## build as Docker container

        cd docker/
        docker-compose -f croustibatch.yml up