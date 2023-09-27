from django.test import TestCase

from nstv.models import Show


class DeleteShowTestCase(TestCase):
    def setUp(self):
        # Create a record before each test
        self.dummy_show_record = Show.objects.create(title='Dummy show to be deleted.')

    def tearDown(self):
        # Delete the record after each test
        self.dummy_show_record.delete()

    def test_delete_show(self):
        self.client.post('/delete/{}'.format(self.dummy_show_record.id))
        with self.assertRaises(Show.DoesNotExist):
            Show.objects.get(title='Dummy show to be deleted.')

    def test_delete_show_GET_request_fails(self):
        with self.assertRaises(Exception):
            self.client.get('/delete/{}'.format(self.dummy_show_record.id))
