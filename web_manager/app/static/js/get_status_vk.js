// узнаем статус при загрузке документа
$(document).ready(function () {
    check_vk_bot_status();
});

// если кликнут по кнопке, то узнаем сатус
$('#vk-bot-status-btn').click(function () {
    check_vk_bot_status()
});


function check_vk_bot_status() {

    // скрываем информацию о статусе
    $('#vk-bot-status-info').hide();
    // показываем анимацию загрузки
    $('#vk-bot-status-loading').show();

    $.ajax({
        url: '/vk-bot/status',
        success: function (data, textStatus) {
            console.log(data);
            console.log(textStatus)

            // скрываем загрузку
            $('#vk-bot-status-loading').hide();
            // устанавливаем картинку Включено
            $("#vk-bot-status-img").attr("src", "/static/img/on.jpg");
            //пишем текст Активен
            $("#vk-bot-status-text").text('Активен')
            // Показываем статус
            $('#vk-bot-status-info').show();

        },
        error: function (data, textStatus) {
            // скрываем загрузку
            $('#vk-bot-status-loading').hide();
            // устанавливаем картинку Включено
            $("#vk-bot-status-img").attr("src", "/static/img/off.jpg");
            //пишем текст Не активен
            $("#vk-bot-status-text").text('Не активен')
            // Показываем статус
            $('#vk-bot-status-info').show();
        }
    });


}