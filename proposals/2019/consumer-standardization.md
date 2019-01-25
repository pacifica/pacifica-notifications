# Consumer Standardization

## Overview

This proposal standardizes the behavior of consumers of CloudEvents notifications (corresponding to Pacifica transactions).

## Justification

The behavior of consumers of CloudEvents notifications (corresponding to Pacifica transactions) is not standardized.

## Implementation

### How do I develop a consumer?

1. Optionally, develop a shell script that will initialize the environment for the consumer (i.e., that will install any requirements that cannot be listed in a Python3 requirements file).
  * The filename of the shell script is `./init.sh`.
  * If the shell script file is not present, then the system assumes that it is empty.

2. Optionally, develop a Python3 requirements file for the consumer.
  * The filename for the requirements file is `./requirements.txt`.
  * If the requirements file is not present, then the system assumes that it is empty.

3. Develop a JSONPath to be tested against the JSON object for a given CloudEvents notification (corresponding to a given Pacifica transaction).
  * The filename for the JSONPath is `jsonpath2.txt`.
  * The usage of the JSONPath is as follows:
    * If the test returns a non-empty result set, then the consumer will be notified.
    * If the test returns an empty result set, then the consumer will not be notified.

4. Develop a top-level Python3 script (viz., the entry-point) that will be executed by the consumer within a virtual environment.
   The behavior of the entry-point is to act upon a given CloudEvents notification for a given Pacifica transaction (and its associated input data files and key-value pairs) and then to generate a new Pacifica transaction (and its associated output data files and key-value pairs).
   The Pacifica transaction for the output data files preserves the `Transactions.submitter`, `Transactions.proposal` and `Transactions.instrument` attributes of the Pacifica transaction for the input data files.
  * The filename of the entry-point is `./__main__.py`.
  * The input data files (downloaded from Pacifica) are located in the `./downloads/` subdirectory.
  * The output data files (uploaded to Pacifica) are located in the `./uploads/` subdirectory.
  * The JSON object for the CloudEvents notification is `./notification.json`.
  * The JSON object for the Pacifica transaction key-value pairs for the input data files is `./metadata-downloads.json`.
  * The JSON object for the Pacifica transaction key-value pairs for the output data files is `./metadata-uploads.json`.
    * The JSON object for the Pacifica transaction key-value pairs for the output data files must include a `Transactions._id` key, where the value is the identifier of the Pacifica transaction for the input data files; **the value is set automatically**.
  * The execution of the entry-point terminates with the following exit status codes:
    * `0` = Terminated successfully; create a new Pacifica transaction.
    * `1` = Terminated successfully; do not create a new Pacifica transaction.
    * `>1` = Terminated unsuccessfully; do not create a new Pacifica transaction.

5. Compress the entry-point, the requirements file, the JSONPath file and any additional files that are necessary for execution of the entry-point into a zip archive called `consumer.zip`.

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

The JSONPath returns a list of filenames for input data files whose MIME type is `text/plain`.
```
$[?(@["eventID"] and (@["eventType"] = "org.pacifica.metadata.ingest") and (@["source"] = "/pacifica/metadata/ingest"))]["data"][*][?((@["destinationTable"] = "Files") and (@["mimetype"] = "text/plain"))]["name"]
```

##### `requirements.txt`

The requirements file specifies the JSONPath [1] package.
```
jsonpath2
```

##### `__main__.py`

The entry-point is as follows:
```python
#!/usr/bin/env python3

import json
import os
import sys

import jsonpath2

# execute only if run as a top-level script
if __name__ == "__main__":
  # open file for key-value pairs for output data files
  with open("metadata-uploads.json", "w") as json_file:
    # key-value pairs
    data = {
      "SoftwareName": "upper",
      "SoftwareVersion": "0.0.1",
      "Documentation": "https://docs.python.org/3/library/stdtypes.html#str.upper",
    }

    # write JSON object for key-value pairs to file
    json.dump(data, json_file)

  # read and parse JSONPath file
  path = jsonpath2.parse_file("jsonpath2.txt")

  # open CloudEvents notification file
  with open("notification.json", "r") as notification_file:
    # read JSON object for CloudEvents notification
    notification_data = json.load(notification_file)

    # iterate over JSONPath match results
    for match_result in path.match(notification_data):
      # match result "value" attribute is the filename for the input data file
      filename = match_result.value

      # open input data file
      with open(os.path.join("downloads", filename), "r") as orig_file:
        # open output data file
        with open(os.path.join("uploads", filename), "w") as new_file:
          # read input data file, convert cased characters to uppercase, and then write output data file
          new_file.write(orig_file.read().upper())

  # terminate successfully; create new Pacifica transaction
  sys.exit(0)
```

### How do I deploy a consumer

1.	Download and install the `pacifica-notifications` package.
  * When the `pacifica-notifications` is successfully installed, the `start-pacifica-notifications-consumer` command is available on the `PATH`.
  * When started, the behavior of the `start-pacifica-notifications-consumer` command is to: (i) extract the contents of `consumer.zip` to a temporary location, (ii) create a new virtual environment, (iii) install the contents of the requirements file within said virtual environment, (iv) start a new asynchronous job processing queue, (v) start a new web service end-point for a new consumer, and (vi) register said web service end-point for said consumer with the given producer.
  * When stopped, the behavior of the `start-pacifica-notifications-consumer` command is reverse the side-effects of the start-up behavior (i.e., to clean up after itself).

2.	Execute the `start-pacifica-notifications-consumer` command, specifying as command-line arguments:
  * The location of `consumer.zip`;
  * The URL and authentication credentials for the producer; and
  * The configuration for the asynchronous job processing queue, web service end-point, etc.

## Open Questions (to be addressed by this proposal)

* How should non-Python programming languages be handled?
  * In principal, non-Python programming languages could be called from the Python entry-point.
  * In practice, it may be beneficial to maintain separate `pacifica-notifications` ports for each programming language.

* How to handle authentication and/or authorization?

* How to handle blocking on two-or-more CloudEvents notifications (i.e., to receive the first CloudEvents notification and then wait for the successive CloudEvents notifications)?

* Should locally-generated files be persisted after the entry-point has terminated?

* Should the `start-pacifica-notifications-consumer` command provide additional functionality (e.g., to specify a list of key-value pairs that are to be appended to every Pacifica transaction, e.g., the exit status code, the project name, the project charge code, etc.)?

## Glossary of Terms

*	__Consumer:__ A software system that receives CloudEvents notifications (corresponding to Pacifica transactions) from producers. CloudEvents notifications are filtered by testing against a JSONPath [1]. If the test for a given CloudEvents notification is successful, then the consumer routes said CloudEvents notification to a processor.
*	__Processor:__ A software system that downloads the input data files and metadata for a given Pacifica transaction, processes said input data files and associated metadata, generates output data files and associated metadata, and then creates a new Pacifica transaction.
* __Producer:__ A software system that sends CloudEvents notifications (corresponding to Pacifica transactions) to consumers.

## References

1. "JSONPath implementation for Python" https://pypi.org/project/jsonpath2/
