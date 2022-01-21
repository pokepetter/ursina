
event_update = []
event_input = []
event_key_input = []

def _append_event(entity, append, event_list):
    contained = entity in event_list

    if not append and contained:
        event_list.remove(entity)

    elif append and not contained:
        event_list.append(entity)

def append_update_event(entity, append = True):
    _append_event(entity, append, event_update)

def append_input_event(entity, append = True):
    _append_event(entity, append, event_input)

def append_keystroke_event(entity, append = True):
    _append_event(entity, append, event_key_input)