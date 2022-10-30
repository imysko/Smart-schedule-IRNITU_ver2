def processing_api(bot, message):
    chat_id = message.chat.id
    text = message.text

    match text:
        case '/api/institutes':
            pass
        case '/api/groups':
            pass
        case '/api/lessons_time':
            pass
        case '/api/teachers':
            pass
        case '/api/lessons_names':
            pass
        case '/api/schedule/two_weeks':
            pass
        case '/api/schedule/year':
            pass
