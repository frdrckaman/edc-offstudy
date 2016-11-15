from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from django.utils import timezone


from django.test.testcases import TestCase

from edc_example.models import (
    SubjectVisit, Appointment, Enrollment)
from edc_example.factories import SubjectConsentFactory, SubjectVisitFactory


from edc_constants.constants import ON_STUDY, OFF_STUDY
from edc_offstudy.constants import OFF_STUDY_REASONS
from edc_example.models import SubjectOffStudy, CrfOne

from edc_visit_tracking.constants import SCHEDULED
from edc_offstudy.model_mixins import OffStudyError


class TestOffStudy(TestCase):

    def setUp(self):
        self.subject_consent = SubjectConsentFactory()
        Enrollment.objects.create(subject_identifier=self.subject_consent.subject_identifier)
        self.appointment = Appointment.objects.get(
            visit_code='1000'
        )
        self.subject_visit = SubjectVisitFactory(
            appointment=self.appointment,
            visit_schedule_name='subject_visit_schedule',
            schedule_name='schedule-1',
            report_datetime=timezone.now() - relativedelta(weeks=4),
            study_status=SCHEDULED
        )

    def test_create_off_study(self):
        SubjectOffStudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today() - relativedelta(weeks=3)
        )
        self.assertEqual(1, SubjectOffStudy.objects.all().count())

    def test_is_off_study_or_raise(self):
        SubjectOffStudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today() - relativedelta(weeks=3)
        )
        with self.assertRaises(OffStudyError) as cm:
            CrfOne.objects.create(
                subject_visit=self.subject_visit
            )
        self.assertIn('Participant was reported off study on', str(cm.exception))

    def test_is_off_study_or_raise_new_visits(self):
        SubjectOffStudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today() - relativedelta(weeks=3)
        )
        with self.assertRaises(OffStudyError) as cm:
            SubjectVisit.objects.create(
                appointment=self.appointment,
                report_datetime=timezone.now())
        self.assertIn('Participant was reported off study on', str(cm.exception))

    def test_off_study_on_delete_future_appts(self):
        SubjectOffStudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now() - relativedelta(weeks=4),
            offstudy_date=date.today() - relativedelta(weeks=3),
            reason=OFF_STUDY,
        )
        self.assertEqual(1, Appointment.objects.all().count())

    def test_off_study_on_delete_future_appts1(self):
        appointment = Appointment.objects.get(
            visit_code='2000'
        )
        SubjectVisitFactory(
            appointment=appointment,
            visit_schedule_name='subject_visit_schedule',
            schedule_name='schedule-1',
            report_datetime=timezone.now() - relativedelta(weeks=3),
            study_status=SCHEDULED
        )
        SubjectOffStudy.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            report_datetime=timezone.now() - relativedelta(weeks=3),
            offstudy_date=date.today() - relativedelta(weeks=3),
            reason=OFF_STUDY,
        )
        self.assertEqual(2, Appointment.objects.all().count())
