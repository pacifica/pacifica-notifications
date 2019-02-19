# Consumer Expectations

## Implementation

### How do I develop a consumer?

1. Optionally, develop a shell script that will initialize the environment for the consumer (i.e., that will install any requirements that cannot be listed in a [Python3](https://www.python.org/) requirements file).
  * The filename of the shell script is `./init.sh`.
  * If the shell script file is not present, then the system assumes that it is empty.

2. Optionally, develop a [Python3](https://www.python.org/) requirements file for the consumer.
  * The filename for the requirements file is `./requirements.txt`.
  * If the requirements file is not present, then the system assumes that it is empty.

3. Develop a [JSONPath](https://pypi.org/project/jsonpath2/) to be tested against the [JSON](http://json.org/) object for a given [CloudEvents](https://cloudevents.io/) notification (corresponding to a given Pacifica transaction).
  * The filename for the [JSONPath](https://pypi.org/project/jsonpath2/) is `jsonpath2.txt`.
  * The usage of the [JSONPath](https://pypi.org/project/jsonpath2/) is as follows:
    * If the test returns a non-empty result set, then the consumer will be notified.
    * If the test returns an empty result set, then the consumer will not be notified.

4. Develop a top-level [Python3](https://www.python.org/) script (viz., the entry-point) that will be executed by the consumer within a virtual environment.
   The behavior of the entry-point is to act upon a given [CloudEvents](https://cloudevents.io/) notification for a given Pacifica transaction (and its associated input data files and key-value pairs) and then to generate a new Pacifica transaction (and its associated output data files and key-value pairs).
  * The filename of the entry-point is `./__main__.py`.
  * The usage of the entry-point is `./__main__.py SRC DST`, where:
    * `SRC` is the path to the temporary directory for the incoming Pacifica transaction.
    * `DST` is the path to the temporary directory for the outgoing Pacifica transaction.
  * The input data files (downloaded from Pacifica) are located in the `SRC/downloads/` subdirectory.
  * The output data files (uploaded to Pacifica) are located in the `DST/uploads/` subdirectory.
  * The [JSON](http://json.org/) object for the [CloudEvents](https://cloudevents.io/) notification is `SRC/notification.json`.
  * The execution of the entry-point terminates with the following exit status codes:
    * `0` = Terminated successfully.
    * `>0` = Terminated unsuccessfully.

5. Compress the entry-point, the requirements file, the [JSONPath](https://pypi.org/project/jsonpath2/) file and any additional files that are necessary for execution of the entry-point into a zip archive called `consumer.zip`.

#### Example implementation of a consumer

In this example, we develop a consumer that copies the input data files with all cased characters converted to uppercase.

##### `consumer.zip`

The directory-tree listing for `consumer.zip` is as follows:
* `/`
  * `init.sh`
  * `jsonpath2.txt`
  * `requirements.txt`
  * `__main__.py`

##### `init.sh`

The shell script does nothing.
```bash
#!/usr/bin/env sh

exit 0
```

##### `jsonpath2.txt`

The [JSONPath](https://pypi.org/project/jsonpath2/) returns the set of IDs for input data files whose MIME type is `text/plain`.
```
$[?(@["eventID"] and (@["eventType"] = "org.pacifica.metadata.ingest") and (@["source"] = "/pacifica/metadata/ingest"))]["data"][*][?((@["destinationTable"] = "Files") and (@["mimetype"] = "text/plain"))]["_id"]
```

##### `requirements.txt`

The requirements file specifies the [JSONPath](https://pypi.org/project/jsonpath2/), Pacifica notification service consumer and [Promise](https://pypi.org/project/promise/) packages.
```
jsonpath2
pacifica-notifications-consumer
promises
```

##### `__main__.py`

The entry-point is as follows:
```python
#!/usr/bin/env python3

import json
import os
import shutil
import sys

from jsonpath2 import Path
from pacifica_notifications_consumer import download, upload
from promise import Promise

# execute only if run as a top-level script
if __name__ == '__main__':
  # path to directory for input CloudEvents notification
  orig_event_path = sys.argv[1]

  # path to directory for output CloudEvents notification
  new_event_path = sys.argv[2]

  def upload_did_fulfill(d):
    """Callback for Pacifica uploader promise's eventual value.

    Args:
        d (dict): CloudEvents notification.

    Returns:
        Promise[bool]: True for success, False otherwise.

    Raises:
        BaseException: If an error occurs.
    """

    # delete entire directory tree for input CloudEvents notification
    shutil.rmtree(orig_event_path, ignore_errors=True)

    # delete entire directory tree for output CloudEvents notification
    shutil.rmtree(new_event_path, ignore_errors=True)

    # return True for success
    return Promise(lambda resolve, reject: resolve(True))

  def download_did_fulfill(d):
    """Callback for Pacifica downloader promise's eventual value.

    Args:
        d (dict): CloudEvents notification.

    Returns:
        Promise[bool]: True for success, False otherwise.

    Raises:
        BaseException: If an error occurs.
    """

    # iterate over plain-text files
    for file_d in [ match_data.current_value for match_data in Path.parse_str('$["data"][*][?(@["destinationTable"] = "Files" and @["mimetype"] = "text/plain")]').match(d) ]:
      # open input data file
      with open(os.path.join(orig_event_path, 'downloads', file_d['subdir'], file_d['name']), 'r') as orig_file:
        # open output data file
        with open(os.path.join(new_event_path, 'uploads', file_d['subdir'], file_d['name']), 'w') as new_file:
          # read input data file, convert cased characters to uppercase, and then write output data file
          new_file.write(orig_file.read().upper())

    # invoke Pacifica uploader with specified transaction attributes and key-value pairs
    return upload(new_event_path, {
      'Transactions.instrument': [ match_data.current_value for match_data in Path.parse_str('$["data"][*][?(@["destinationTable"] = "Transactions.instrument")]["value"]').match(d) ][0],
      'Transactions.proposal': [ match_data.current_value for match_data in Path.parse_str('$["data"][*][?(@["destinationTable"] = "Transactions.proposal")]["value"]').match(d) ][0],
      'Transactions.submitter': [ match_data.current_value for match_data in Path.parse_str('$["data"][*][?(@["destinationTable"] = "Transactions.submitter")]["value"]').match(d) ][0],
    }, {
      'Transactions._id': [ match_data.current_value for match_data in Path.parse_str('$["data"][*][?(@["destinationTable"] = "Transactions._id")]["value"]').match(d) ][0],
    }).then(upload_did_fulfill)

  # invoke Pacifica downloader
  download(orig_event_path).then(download_did_fulfill)
```

### How do I deploy a consumer

1. Download and install the `pacifica-notifications-consumer` package.
  * When the `pacifica-notifications-consumer` is successfully installed, the `start-pacifica-notifications-consumer` command is available on the `PATH`.
  * When started, the behavior of the `start-pacifica-notifications-consumer` command is to: (i) extract the contents of `consumer.zip` to a temporary location, (ii) create a new virtual environment, (iii) install the contents of the requirements file within said virtual environment, (iv) start a new asynchronous job processing queue, (v) start a new web service end-point for a new consumer, and (vi) register said web service end-point for said consumer with the given producer.
  * When stopped, the behavior of the `start-pacifica-notifications-consumer` command is reverse the side-effects of the start-up behavior (i.e., to clean up after itself).

2. Execute the `start-pacifica-notifications-consumer` command, specifying as command-line arguments:
  * The location of `consumer.zip`;
  * The URL and authentication credentials for the producer; and
  * The configuration for the asynchronous job processing queue, web service end-point, etc.

## Frequently Asked Questions

### Are downloaded files persisted after the entry-point for a consumer has terminated?

Yes. Downloaded files may be deleted by the entry-point (e.g., using the `shutil.rmtree` method; see `__main__.py` in the example).

### Are locally-generated files persisted after the entry-point for a consumer has terminated?

Yes. Locally-generated files may be deleted by the entry-point (e.g., using the `shutil.rmtree` method; see `__main__.py` in the example).

### Can I develop the entry-point for a consumer to wait for two-or-more CloudEvents notifications?

Yes. However, this behavior must be implemented by the entry-points themselves and is not provided by the default behavior of the `start-pacifica-notifications-consumer` command.

For example, to wait for two [CloudEvents](https://cloudevents.io/) notifications:
* Develop two consumers with two entry-points.
* The entry-point for the first consumer receives and stores the first [CloudEvents](https://cloudevents.io/) notification.
* The entry-point for the second consumer receives the second [CloudEvents](https://cloudevents.io/) notification, retrieves the first [CloudEvents](https://cloudevents.io/) notification, and then does its work.

### Can I develop the entry-point for a consumer using a non-Python3 programming language?

No. Only [Python3](https://www.python.org/) is supported as the programming language for the entry-point file (viz., `__main__.py`).

Non-[Python3](https://www.python.org/) executables can be called from within the entry-point using the [`subprocess`](https://docs.python.org/3/library/subprocess.html) module.

Other programming languages can be called from within the entry-point using the appropriate interface, e.g., the [`jpy`](https://pypi.org/project/jpy/) package for the Java programming language, and the [`rpy2`](https://pypi.org/project/rpy2/) package for the R programming language.

### How do I authenticate with the CloudEvents notification provider?

Authentication credentials are specified in the configuration for the `pacifica-notifications` package (see https://pacifica-notifications.readthedocs.io/en/latest/configuration.html for more information).

Authentication credentials are included in all HTTP requests that are issued by the consumer, e.g., the username is specified via the `Http-Remote-User` header (see https://pacifica-notifications.readthedocs.io/en/latest/exampleusage.html for more information).

## Glossary of Terms

 * __Consumer:__ A software system that receives [CloudEvents](https://cloudevents.io/) notifications (corresponding to Pacifica transactions) from producers. [CloudEvents](https://cloudevents.io/) notifications are filtered by testing against a [JSONPath](https://pypi.org/project/jsonpath2/). If the test for a given [CloudEvents](https://cloudevents.io/) notification is successful, then the consumer routes said [CloudEvents](https://cloudevents.io/) notification to a processor.
 * __Processor:__ A software system that downloads the input data files and metadata for a given Pacifica transaction, processes said input data files and associated metadata, generates output data files and associated metadata, and then creates a new Pacifica transaction.
 * __Producer:__ A software system that sends [CloudEvents](https://cloudevents.io/) notifications (corresponding to Pacifica transactions) to consumers.
