// узнаем статус при загрузке документа
$(document).ready(function () {
    check_tg_bot_status();
    check_parser_status();
    check_notifications_tg_status();
    check_notifications_vk_status();
});

/* telegram бот */
// если кликнут по кнопке, то узнаем статус
$('#tg-bot-status-btn').click(function () {
    check_tg_bot_status()
});


function check_tg_bot_status() {
    // скрываем информацию о статусе
    $('#tg-bot-status-info').hide();
    // показываем анимацию загрузки
    $('#tg-bot-status-loading').show();

    $.ajax({
        url: '/telegram-bot/status',
        success: function (data, textStatus) {
            console.log(data);
            console.log(textStatus)

            // скрываем загрузку
            $('#tg-bot-status-loading').hide();
            // устанавливаем картинку Включено
            $("#tg-bot-status-img").attr("src", "/static/img/on.jpg");
            //пишем текст Активен
            $("#tg-bot-status-text").text('Активен')
            // Показываем статус
            $('#tg-bot-status-info').show();

        },
        error: function (data, textStatus) {
            // скрываем загрузку
            $('#tg-bot-status-loading').hide();
            // устанавливаем картинку Включено
            $("#tg-bot-status-img").attr("src", "/static/img/off.jpg");
            //пишем текст Не активен
            $("#tg-bot-status-text").text('Не активен')
            // Показываем статус
            $('#tg-bot-status-info').show();
        }
    });
}
/* telegram бот end*/


/* Парсер бот */
// если кликнут по кнопке, то узнаем статус
$('#parser-status-btn').click(function () {
    check_parser_status()
});


function check_parser_status() {
    // скрываем информацию о статусе
    $('#parser-status-info').hide();
    // показываем анимацию загрузки
    $('#parser-status-loading').show();

    $.ajax({
        url: '/status/parser',
        success: function (data, textStatus) {
            console.log(data);
            console.log(textStatus)

            // скрываем загрузку
            $('#parser-status-loading').hide();
            // устанавливаем картинку Включено
            $("#parser-status-img").attr("src", "/static/img/on.jpg");
            //пишем текст Активен
            $("#parser-status-text").text('Активен')
            // Показываем статус
            $('#parser-status-info').show();

        },
        error: function (data, textStatus) {
            // скрываем загрузку
            $('#parser-status-loading').hide();
            // устанавливаем картинку Включено
            $("#parser-status-img").attr("src", "/static/img/off.jpg");
            //пишем текст Не активен
            $("#parser-status-text").text('Не активен')
            // Показываем статус
            $('#parser-status-info').show();
        }
    });
}
/* Парсер end*/

/* Уведомления TG бот */
// если кликнут по кнопке, то узнаем статус
$('#notification_tg-status-btn').click(function () {
    check_notifications_status()
});


function check_notifications_tg_status() {
    // скрываем информацию о статусе
    $('#notification_tg-status-info').hide();
    // показываем анимацию загрузки
    $('#notification_tg-status-loading').show();

    $.ajax({
        url: '/status/tg_reminders',
        success: function (data, textStatus) {
            console.log(data);
            console.log(textStatus)

            // скрываем загрузку
            $('#notification_tg-status-loading').hide();
            // устанавливаем картинку Включено
            $("#notification_tg-status-img").attr("src", "/static/img/on.jpg");
            //пишем текст Активен
            $("#notification_tg-status-text").text('Активен')
            // Показываем статус
            $('#notification_tg-status-info').show();

        },
        error: function (data, textStatus) {
            // скрываем загрузку
            $('#notification_tg-status-loading').hide();
            // устанавливаем картинку Включено
            $("#notification_tg-status-img").attr("src", "/static/img/off.jpg");
            //пишем текст Не активен
            $("#notification_tg-status-text").text('Не активен')
            // Показываем статус
            $('#notification_tg-status-info').show();
        }
    });
}
/* Уведомления end*/

/* Уведомления VK бот */
// если кликнут по кнопке, то узнаем статус
$('#notification_vk-status-btn').click(function () {
    check_notifications_status()
});

function check_notifications_vk_status() {
    // скрываем информацию о статусе
    $('#notification_vk-status-info').hide();
    // показываем анимацию загрузки
    $('#notification_vk-status-loading').show();

    $.ajax({
        url: '/status/vk_reminders',
        success: function (data, textStatus) {
            console.log(data);
            console.log(textStatus)

            // скрываем загрузку
            $('#notification_vk-status-loading').hide();
            // устанавливаем картинку Включено
            $("#notification_vk-status-img").attr("src", "/static/img/on.jpg");
            //пишем текст Активен
            $("#notification_vk-status-text").text('Активен')
            // Показываем статус
            $('#notification_vk-status-info').show();

        },
        error: function (data, textStatus) {
            // скрываем загрузку
            $('#notification_vk-status-loading').hide();
            // устанавливаем картинку Включено
            $("#notification_vk-status-img").attr("src", "/static/img/off.jpg");
            //пишем текст Не активен
            $("#notification_vk-status-text").text('Не активен')
            // Показываем статус
            $('#notification_vk-status-info').show();
        }
    });
}
/* Уведомления end*/