=============
Server Status
=============

The Server Status page in the Phagescan web interface provides a status display of each of the celery queues; this includes queues for engines and the master.

For the engine queues, there are 2 columns. The first column displays the number of workers that are on-line, have a queue for that engine, and are under the management of Phagescan. The second column simply displays the number of queues that are running for each engine. In a production environment, both columns should be equal. In a development environment, it can vary.

Starting a Worker
=================

When Phagescan is first started, both columns will show zero active queues. The first column will have an UP ARROW icon next to each engine queue. To start a worker and thus the queues for a set of engines, click the UP ARROW icon. Many of the queues are handle by a single worker, so clicking the UP ARROW next to one queue per worker type is sufficient. When starting a worker, Phagescan will start 1 or more actual worker VMs. The number of VMs per worker type is configured in the ADMIN interface. (PUT REFERENCE TO ADMIN INTERFACE HERE) Starting a new set of workers can take several minutes, so be patient. 

For example, the current design has three (3) worker types: Ubuntu, CentOS, and WinXP. The WinXP worker only handles the Panda engine. The CentOS worker only handles the Symantec engine. The Ubuntu worker handles the rest of the engines. So, in this example, you would start all workers and thus queues by clicking three UP ARROWs. 1) Symantec, 2) Panda, and 3) One of any other engine.

Stopping a Worker
=================

When Phagescan is up and running, both columns will show active queues. The first column will have a RED X icon next to each engine queue. To stop a worker and thus the queues for the set of engines on that worker, click the RED X icon. This will shutdown and destroy all of the VMs for the worker type associated with that queue. 

For example, the current design has three VMs running for the Ubuntu worker type. If you click the RED X, it will destroy all 3 VMs.
