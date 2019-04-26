This is the source distribution of Ostfalia-Praktomat, a programming course manager which can also be used as a simple 
grading backend for different programming languages. 

The code is an old fork (2012) from the KIT Praktomat (https://github.com/KITPraktomatTeam/Praktomat).
It adds the ProFormA interface (https://github.com/ProFormA/proformaxml) which enables Praktomat 
to be used as a grading back-end in e.g. learning management systems. 

The code is currently only used as a 'docker composition'. 
So the installation manual is not up-to-date.

Docker 
============

In order to set up the docker composition execute the following steps:

* build the docker images (call 'docker-compose build')

* start the docker containers (call 'docker-compose up')

* initialise the docker containers (call 'docker exec -ti praktomat ./init_database.sh')

Then Praktomat is available on port 80 in your web browser.  

        http://localhost

If you only want to use the Praktomat as a grading back-end the appropriate URI is

        http://localhost:80/api/v2/submissions

or (circumventing the web server)

        http://localhost:8010/api/v2/submissions 



ProFormA API (CURL)
============

The supported ProFormA format version is 2.0. 

A typical grading HTTP request in CURL is

    curl -X POST --form submission.xml=@submission.xml -F "{solutionfilename}=@{solutionfile}" -F "{taskfilename}=@{taskfile}" http://localhost:8010/api/v2/submissions

with the following 'submission.xml'
    
    <?xml version="1.0" encoding="utf-8"?>
    <submission xmlns="urn:proforma:v2.0">
        <external-task uuid="{UUID}">http-file:{taskfilename}</external-task>
        <external-submission>http-file:{solutionfilename}</external-submission>
        <lms url="{your URI}">
            <submission-datetime>{timestamp}</submission-datetime>
            <user-id>{user id}</user-id>
            <course-id>{course id}</course-id>
        </lms>
        <result-spec format="xml" structure="separate-test-feedback" lang="de">
            <student-feedback-level>{level}</student-feedback-level>
            <teacher-feedback-level>{level}</teacher-feedback-level>
        </result-spec>
    </submission>"

'submission.xml' can be transferred as a separate file or simply as data.
 
Note that embedding the submission file(s) into submission.xml as embedded-txt-file is also supported.

A sample for a timestamp is: "2019-04-03T01:01:01+01:00". 

