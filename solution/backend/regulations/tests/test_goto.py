from django.test import RequestFactory

from regulations.views.goto import GoToRedirectView


def test_goto_redirect_with_section():
    request = RequestFactory().get("/goto/", {"title": "42", "part": "433", "section": "10"})
    view = GoToRedirectView()
    view.setup(request)

    assert view.get_redirect_url() == "/42/433/10/#433-10"


def test_goto_redirect_without_section():
    request = RequestFactory().get("/goto/", {"title": "42", "part": "433"})
    view = GoToRedirectView()
    view.setup(request)

    assert view.get_redirect_url() == "/42/433/full/"


def test_goto_redirect_with_empty_section():
    request = RequestFactory().get("/goto/", {"title": "42", "part": "433", "section": ""})
    view = GoToRedirectView()
    view.setup(request)

    assert view.get_redirect_url() == "/42/433/full/"
