from mocker import ANY
from mocker import MockerTestCase
from watchlist.utils import confirmation_prompt


class TestConfirmationPrompt(MockerTestCase):

    def setUp(self):
        super(TestConfirmationPrompt, self).setUp()

        self.raw_input_mock = self.mocker.replace(raw_input)

    def test_confirm_with_yes(self):
        self.type_when_asked('Yes', 'Are you sure? [Yes/No]')
        self.mocker.replay()
        self.assertTrue(confirmation_prompt('Are you sure?'))

    def test_confirm_with_y(self):
        self.type_when_asked('y', 'Are you sure? [Yes/No]')
        self.mocker.replay()
        self.assertTrue(confirmation_prompt('Are you sure?'))

    def test_confirm_with_no(self):
        self.type_when_asked('No', 'Are you sure? [Yes/No]')
        self.mocker.replay()
        self.assertFalse(confirmation_prompt('Are you sure?'))

    def test_confirm_with_n(self):
        self.type_when_asked('n', 'Are you sure? [Yes/No]')
        self.mocker.replay()
        self.assertFalse(confirmation_prompt('Are you sure?'))

    def test_keeps_asking_until_answer_is_valid(self):
        self.type_when_asked('', 'Are you sure? [Yes/No]')
        self.type_when_asked('invalid', 'Are you sure? [Yes/No]')
        self.type_when_asked('yes', 'Are you sure? [Yes/No]')
        self.mocker.replay()
        self.assertTrue(confirmation_prompt('Are you sure?'))

    def type_when_asked(self, answer, prompt=ANY):
        self.expect(self.raw_input_mock(prompt)).result(answer)
