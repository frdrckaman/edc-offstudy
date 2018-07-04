[![Build Status](https://travis-ci.com/clinicedc/edc-offstudy.svg?branch=develop)](https://travis-ci.com/clinicedc/edc-offstudy)
[![Coverage Status](https://coveralls.io/repos/clinicedc/edc-offstudy/badge.svg)](https://coveralls.io/r/clinicedc/edc-offstudy)

# edc-offstudy

Base classes for off study process


The offstudy model is linked to scheduled models by the visit schedule.

    # visit_schedule.py
    ...
    visit_schedule1 = VisitSchedule(
        name='visit_schedule1',
        offstudy_model='edc_offstudy.subjectoffstudy',
        ...)
    ...


This module includes an offstudy model `SubjectOffstudy`.

You may also declare your own using the `OffstudyModelMixin`:

    class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):
        
         pass
         
If you declare your own, be sure to reference it correctly in the visit schedule:

    # visit_schedule.py
    ...
    visit_schedule1 = VisitSchedule(
        name='visit_schedule1',
        offstudy_model='myapp.subjectoffstudy',
        ...)
    ...


When the offstudy model is saved, the data is validated relative to the consent and __visit model__. An offstudy datetime should make sense relative to these model instances for the subject.

Unused appointments in the future relative to the offstudy datetime will be removed.

> Note: There is some redundancy with this model and the offschedule model from `edc-visit-schedule`. This needs to be resolved.
