from typing import List, Set

from apartment.models import Apartment
from application_form.enums import ApplicationState
from application_form.models import (
    Application,
    ReservationQueue,
    ReservationQueueApplication,
)


def get_ordered_applications(apartment: Apartment) -> List[Application]:
    """
    Returns a list of all applications for the given apartment, ordered by their
    position in the queue. Note that the position in the queue may not directly
    correspond to the right of residence number, e.g. late applications will be
    last even if they have a smaller right of residence number.
    """
    try:
        queue_applications = Application.objects.filter(
            queue_applications__queue=apartment.queue
        ).order_by("queue_applications__queue_position")
        return list(queue_applications)
    except ReservationQueue.DoesNotExist:
        return []


def reserve_haso_apartment(apartment: Apartment) -> Set[Application]:
    # Make sure that the apartment does not have any applications in its queue
    # that have already won another apartment with higher priority.
    _delete_applications_that_already_won(apartment)

    # Get the applications in the queue, ordered by their queue position
    applications = get_ordered_applications(apartment)

    # There can be either a single winner, or multiple winners if there are several
    # applications with the same right of residence number. Applications with duplicate
    # right of residence numbers are marked as "REVIEW". Otherwise, the winning
    # application will be marked as "RESERVED".
    winning_applications = _find_winning_candidates(applications)
    state = ApplicationState.RESERVED
    if len(winning_applications) > 1:
        state = ApplicationState.REVIEW
    for application in winning_applications:
        application.set_state(apartment, state)
    # At this point the winner has been decided, but the winner may have outstanding
    # applications to other apartments. If they are lower priority, they should be
    # deleted from the respective queues.
    _reject_lower_priority_applications(winning_applications, apartment)
    return winning_applications


def _reject_lower_priority_applications(
    applications: Set[Application],
    reserved_apartment: Apartment,
):
    for app in applications:
        reserved_priority = app.applicationapartment_set.get(
            apartment=reserved_apartment
        ).priority_number
        queue_apps = app.queue_applications
        queue_apps.exclude(queue__apartment=reserved_apartment).filter(
            application__applicationapartment__priority_number__gt=reserved_priority,
            application__applicationapartment__state=ApplicationState.SUBMITTED,
        ).delete()
        app_apartments = app.applicationapartment_set.all()
        for app_apartment in app_apartments:
            if (
                app_apartment.priority_number > reserved_priority
                and app_apartment.state == ApplicationState.SUBMITTED
            ):
                app.set_state(app_apartment.apartment, ApplicationState.REJECTED)


def _find_winning_candidates(applications: List[Application]) -> Set[Application]:
    """Return all applications that have the smallest right of residence number."""
    if not applications:
        return set()
    # Applications are sorted, so the first element has the smallest number
    smallest = applications[0].right_of_residence
    return {app for app in applications if app.right_of_residence == smallest}


def _delete_applications_that_already_won(apartment: Apartment):
    """
    Go through the given applications and remove any application that has already
    won an apartment with a higher priority.
    """
    applications = Application.objects.filter(queue_applications__queue=apartment.queue)
    for app in applications:
        if not app.reserved_apartments:
            continue
        application_apartments = app.applicationapartment_set
        priority = application_apartments.get(apartment=apartment).priority_number
        if not _application_has_higher_priority_reservation(app, priority):
            continue
        # This application won another apartment with a higher priority.
        # For this apartment, the application will be deleted.
        queue_apps = app.queue_applications.filter(queue__apartment=apartment)
        for queue_app in queue_apps:
            position = queue_app.queue_position
            queue_app.delete()
            _shift_queue_positions(apartment.queue, position, deleted=True)


def _application_has_higher_priority_reservation(
    application: Application, priority: int
) -> bool:
    return application.applicationapartment_set.filter(
        apartment__in=application.reserved_apartments,
        priority_number__lt=priority,
    ).exists()


def add_application_to_queue(application: Application, add_to_end: bool = False):
    for apartment in application.apartments.all():
        queue, _ = ReservationQueue.objects.get_or_create(apartment=apartment)
        if add_to_end:
            position = queue.queue_applications.count()
        else:
            position = _calculate_queue_position(queue, application)
            _shift_queue_positions(queue, position)
        ReservationQueueApplication.objects.create(
            queue=queue,
            queue_position=position,
            application=application,
        )


def remove_application_from_queue(application: Application, apartment: Apartment):
    queue_application = application.queue_applications.get(queue__apartment=apartment)
    position = queue_application.queue_position
    queue_application.delete()
    _shift_queue_positions(apartment.queue, position, deleted=True)
    application.set_state(apartment, ApplicationState.REJECTED)


def _calculate_queue_position(queue: ReservationQueue, application: Application) -> int:
    queue_applications = queue.queue_applications.only(
        "application__right_of_residence"
    ).order_by("application__right_of_residence")
    for position, queue_application in enumerate(queue_applications):
        other_application = queue_application.application
        if application.right_of_residence < other_application.right_of_residence:
            return position
    return queue_applications.count()


def _shift_queue_positions(
    queue: ReservationQueue, from_position: int, deleted: bool = False
):
    sort_key = "queue_position" if deleted else "-queue_position"
    position_change = -1 if deleted else 1
    queue_applications = queue.queue_applications.filter(
        queue_position__gte=from_position
    ).order_by(sort_key)
    for queue_application in queue_applications:
        queue_application.queue_position += position_change
    ReservationQueueApplication.objects.bulk_update(
        queue_applications, ["queue_position"]
    )
