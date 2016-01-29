################
CCXCon Test Plan
################

CCXCon is not a user-facing application, so this document will focus on its
API and its integration with Teacher's Portal and edX.

These are the API endpoints:

Courses Collection [/api/v1/coursexs/]
Course [/api/v1/coursexs/{course_uuid}/]
Modules collection [/api/v1/coursexs/{course_uuid}/modules/]
Module [/api/v1/coursexs/{course_uuid}/modules/{module_uuid}/]
CCX Collection [/api/v1/coursexs/{course_uuid}/ccxs]
CCX [/api/v1/coursexs/{course_uuid}/ccxs/{ccx_uuid}]
Modules collection [/api/v1/coursexs/{ccx_uuid}/modules]
Module membership [/api/v1/ccxs/{ccx_uuid}/modules/{module_uuid}]

*******
Courses
*******


============
List Courses
============

.. note::

  You may only list courses if you...

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * - 
     - 
     -
   * - 
     - 
     -

******
Course
******

=============
List a course
=============

.. list-table::
   :widths: 20 35 25
   :header-rows: 1

   * - Action
     - Result
     - Notes
   * -
     -
     -
   * -
     - Course title appears in 'Course' facet list with the total number
       of LRs following the title.
     -
