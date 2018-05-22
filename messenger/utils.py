import datetime

from django.utils import timezone

from messenger.models import ChatMessage, Inbox


def set_data(connection, time_diff_cmp, key, data):
    time_diff = timezone.now() - connection.time
    if time_diff.days <= time_diff_cmp:
        data[key]['connection_request'] += 1
        if connection.is_sent:
            data[key]['connected'] += 1
        if connection.replied_date:
            data[key]['replied'] += 1


def calculate_communication_stats(linkedin_user_id):
    data = {
        'h24': {'connection_request': 0, 'connected': 0, 'replied': 0, 'replied_others': 0},
        'h48': {'connection_request': 0, 'connected': 0, 'replied': 0, 'replied_others': 0},
        'h72': {'connection_request': 0, 'connected': 0, 'replied': 0, 'replied_others': 0},
        'w1': {'connection_request': 0, 'connected': 0, 'replied': 0, 'replied_others': 0},
        'm1': {'connection_request': 0, 'connected': 0, 'replied': 0, 'replied_others': 0},
    }

    connections = ChatMessage.objects.filter(owner__id=linkedin_user_id)

    for connection in connections:
        set_data(connection, 1, 'h24', data)
        set_data(connection, 2, 'h48', data)
        set_data(connection, 3, 'h72', data)
        set_data(connection, 7, 'w1', data)
        set_data(connection, 30, 'm1', data)
    return data


def calculate_connections(linkedin_user_id, status):
    data = {'h24': 0, 'h48': 0, 'h72': 0, 'd7': 0, 'm1': 0}
    connections = Inbox.objects.filter(owner__id=linkedin_user_id, status__in=status)
    for connection in connections:
        if connection.connected_date:
            time_diff = timezone.now() - connection.connected_date
            if time_diff.days <= 1:
                data['h24'] += 1
            if time_diff.days <= 1:
                data['h48'] += 1
            if time_diff.days <= 1:
                data['h72'] += 1
            if time_diff.days <= 7:
                data['d7'] += 1
            if time_diff.days <= 30:
                data['m1'] += 1

    data['connection_count'] = len(connections)
    return data
