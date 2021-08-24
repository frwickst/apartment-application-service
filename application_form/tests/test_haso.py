from pytest import mark

from apartment.tests.factories import ApartmentFactory
from application_form.enums import ApplicationState, ApplicationType
from application_form.haso import (
    add_application_to_queue,
    get_ordered_applications,
    remove_application_from_queue,
    reserve_haso_apartment,
)
from application_form.models import ReservationQueue
from application_form.tests.factories import ApplicationFactory


@mark.django_db
def test_get_ordered_applications_returns_empty_list_when_no_applications():
    # If an apartment has no queue, an empty list should be returned
    assert get_ordered_applications(ApartmentFactory()) == []


@mark.django_db
def test_get_ordered_applications_returns_applications_sorted_by_position():
    # Regardless of the right of residence number of the applications in a queue,
    # they should be returned sorted by their position in the queue.
    apartment = ApartmentFactory()
    app1 = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    app2 = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2)
    app3 = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=3)
    applications = [app3, app1, app2]
    queue = ReservationQueue.objects.create(apartment=apartment)
    for position, app in enumerate(applications):
        queue.queue_applications.create(queue_position=position, application=app)
    assert get_ordered_applications(apartment) == [app3, app1, app2]


@mark.django_db
def test_add_application_to_queue_is_based_on_right_of_residence_number():
    # By default, applications should be added to the queue based
    # on their right of residence number.
    apartment = ApartmentFactory()
    applications = [
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=3),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2),
    ]
    app1, app2, app3 = applications
    for app in applications:
        app.applicationapartment_set.create(apartment=apartment, priority_number=1)
        add_application_to_queue(app)
    assert get_ordered_applications(apartment) == [app2, app3, app1]


@mark.django_db
def test_add_late_application_to_end_of_queue():
    # Late applications should be added to the end of the queue,
    # even if they have a smaller right of residence number.
    apartment = ApartmentFactory()
    applications = [
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=3),
    ]
    for app in applications:
        app.applicationapartment_set.create(apartment=apartment, priority_number=1)
        add_application_to_queue(app)
    late_app = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    late_app.applicationapartment_set.create(apartment=apartment, priority_number=1)
    add_application_to_queue(late_app, add_to_end=True)
    assert get_ordered_applications(apartment) == applications + [late_app]


@mark.django_db
def test_remove_application_from_queue():
    # An application should be removed from the queue and all remaining applications
    # should be moved up by one position each.
    apartment = ApartmentFactory()
    applications = [
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=3),
    ]
    queue = ReservationQueue.objects.create(apartment=apartment)
    for position, app in enumerate(applications):
        app.applicationapartment_set.create(apartment=apartment, priority_number=1)
        queue.queue_applications.create(queue_position=position, application=app)
    assert get_ordered_applications(apartment) == applications
    remove_application_from_queue(applications[0], apartment)
    assert get_ordered_applications(apartment) == applications[1:]


@mark.django_db
def test_reserve_haso_apartment_with_single_application():
    # The single application should win the apartment
    apartment = ApartmentFactory()
    app = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    app.applicationapartment_set.create(apartment=apartment, priority_number=1)
    add_application_to_queue(app)
    winners = reserve_haso_apartment(apartment)
    app.refresh_from_db()
    assert winners == {app}
    assert app.state(apartment) == ApplicationState.RESERVED


@mark.django_db
def test_reserve_haso_apartment_smallest_right_of_residence_number_wins():
    # Smallest right of residence number should win regardless of when it was
    # added to the queue.
    apartment = ApartmentFactory()
    winner = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    applications = [
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2),
        winner,
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=3),
    ]
    for app in applications:
        app.applicationapartment_set.create(apartment=apartment, priority_number=1)
        add_application_to_queue(app)
    assert get_ordered_applications(apartment) == [
        winner,
        applications[0],
        applications[2],
    ]
    assert reserve_haso_apartment(apartment) == {winner}
    winner.refresh_from_db()
    assert winner.state(apartment) == ApplicationState.RESERVED


@mark.django_db
def test_removing_application_from_queue_after_reservation_rejects_application():
    # If an apartment has been reserved for an application but the application is
    # removed from the queue afterwards, the application for the apartment should
    # be marked as rejected, and the next application in the queue should become
    # the new winning candidate.
    apartment = ApartmentFactory()
    old_winner = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    new_winner = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2)
    applications = [old_winner, new_winner]
    for app in applications:
        app.applicationapartment_set.create(apartment=apartment, priority_number=1)
        add_application_to_queue(app)
    assert get_ordered_applications(apartment) == [old_winner, new_winner]
    assert reserve_haso_apartment(apartment) == {old_winner}
    old_winner.refresh_from_db()
    assert old_winner.state(apartment) == ApplicationState.RESERVED
    remove_application_from_queue(old_winner, apartment)
    old_winner.refresh_from_db()
    assert old_winner.state(apartment) == ApplicationState.REJECTED
    assert get_ordered_applications(apartment) == [new_winner]


@mark.django_db
def test_reserve_haso_apartment_multiple_winners_with_same_number():
    # If there are multiple winning candidates with the same right of residence number,
    # they are still treated as "winners", but should be marked as "REVIEW".
    apartment = ApartmentFactory()
    applications = [
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1),
        ApplicationFactory(type=ApplicationType.HASO, right_of_residence=2),
    ]
    for app in applications:
        app.applicationapartment_set.create(apartment=apartment, priority_number=1)
        add_application_to_queue(app)
    assert get_ordered_applications(apartment) == applications
    winners = reserve_haso_apartment(apartment)
    for app in applications:
        app.refresh_from_db()
    assert winners == set(applications[:2])
    assert applications[0].state(apartment) == ApplicationState.REVIEW
    assert applications[1].state(apartment) == ApplicationState.REVIEW
    assert applications[2].state(apartment) == ApplicationState.SUBMITTED


@mark.django_db
def test_reserve_haso_apartment_rejects_lower_priority_applications():
    # If an application wins an apartment, all applications with lower priority
    # should be rejected, as long as that they have not been reserved already
    # for the same application.
    apartment1, apartment2 = [ApartmentFactory(), ApartmentFactory()]
    application = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    application.applicationapartment_set.create(apartment=apartment1, priority_number=1)
    application.applicationapartment_set.create(apartment=apartment2, priority_number=2)
    add_application_to_queue(application)
    assert reserve_haso_apartment(apartment1) == {application}
    application.refresh_from_db()
    assert application.state(apartment1) == ApplicationState.RESERVED
    assert get_ordered_applications(apartment1) == [application]
    assert application.state(apartment2) == ApplicationState.REJECTED
    assert get_ordered_applications(apartment2) == []


@mark.django_db
def test_reserve_haso_apartment_does_not_reject_lower_priority_reservations():
    # If an application wins an apartment but has already won a different apartment
    # with a lower priority, then we should not automatically reject the reserved
    # application despite it being lower priority. This needs to be handled manually
    # by the salespeople.
    apartment1, apartment2 = [ApartmentFactory(), ApartmentFactory()]
    application = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    application.applicationapartment_set.create(apartment=apartment1, priority_number=1)
    application.applicationapartment_set.create(apartment=apartment2, priority_number=2)
    add_application_to_queue(application)
    # Reserve the low priority apartment
    reserve_haso_apartment(apartment2)
    application.refresh_from_db()
    assert application.state(apartment2) == ApplicationState.RESERVED
    assert get_ordered_applications(apartment2) == [application]
    assert application.state(apartment1) == ApplicationState.SUBMITTED
    assert get_ordered_applications(apartment1) == [application]
    # Reserve the high priority apartment
    reserve_haso_apartment(apartment1)
    application.refresh_from_db()
    assert application.state(apartment2) == ApplicationState.RESERVED
    assert get_ordered_applications(apartment2) == [application]
    assert application.state(apartment1) == ApplicationState.RESERVED
    assert get_ordered_applications(apartment1) == [application]


@mark.django_db
def test_reserve_haso_apartment_does_not_reject_higher_priority_applications():
    # If an application wins an apartment with lower priority, then we should not
    # automatically reject submitted applications for apartments with higher priority.
    apartment1, apartment2 = [ApartmentFactory(), ApartmentFactory()]
    application = ApplicationFactory(type=ApplicationType.HASO, right_of_residence=1)
    application.applicationapartment_set.create(apartment=apartment1, priority_number=1)
    application.applicationapartment_set.create(apartment=apartment2, priority_number=2)
    add_application_to_queue(application)
    reserve_haso_apartment(apartment2)
    application.refresh_from_db()
    assert application.state(apartment2) == ApplicationState.RESERVED
    assert get_ordered_applications(apartment1) == [application]
    assert application.state(apartment1) == ApplicationState.SUBMITTED
    assert get_ordered_applications(apartment2) == [application]
