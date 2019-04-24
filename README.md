This is the source distribution of Praktomat, a programming course manager which can also be used as a simple 
grading backend for different programming languages. 

The code is an old fork (2012) from the KIT Praktomat (https://github.com/KITPraktomatTeam/Praktomat).
It adds a ProFormA web interface (https://github.com/ProFormA/proformaxml) which enables Praktomat 
to be used as a grading backend in e.g. learning management systems. 

The source code is currently only used as a 'docker composition'. 
So the installation manual is not up-to-date.

Docker 
============

In order to set up the docker composition execute the following steps:

* build the docker images (call 'docker-compose build')

* start the docker containers (call 'docker-compose up')

* initialise the docker containers (call 'docker exec -ti praktomat ./init_database.sh')

Then Praktomat is available on port 80 (http://localhost).

If you only want to use the Praktomat as a grading backend the REST API is available on port 80 (or without web server on port 8010). 
It complies to ProFormA format version 2.0 (see ) 


ProFormA API (CURL)
============

The grading HTTP request in CURL is

    curl -X POST --form submission.xml=@submission.xml -F "{solutionfilename}=@{solutionfile}" -F "{taskfilename}=@{taskfile}" http://localhost:8010/api/v2/submissions

with the following 'submission.xml'
    
    <?xml version="1.0" encoding="utf-8"?>
    <submission xmlns="urn:proforma:v2.0">
        <external-task uuid="uuid1">http-file:{taskfilename}</external-task>
        <external-submission>http-file:{solutionfilename}</external-submission>
        <lms url="testcase">
            <submission-datetime>1900-01-01T01:01:01+01:00</submission-datetime>
            <user-id>test user</user-id>
            <course-id>test course</course-id>
        </lms>
        <result-spec format="xml" structure="separate-test-feedback" lang="de">
            <student-feedback-level>debug</student-feedback-level>
            <teacher-feedback-level>debug</teacher-feedback-level>
        </result-spec>
    </submission>"

