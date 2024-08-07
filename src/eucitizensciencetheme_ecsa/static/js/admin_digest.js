jQuery(function ($) {
    $('.test').click(function(e){
        e.preventDefault()
        console.log('test')
        console.log($(this).attr('id'))
        $.ajax({
            type: 'POST',
            url: '/digest/sendTest',
            contentType: 'application/json',
            data: {
                content: 'xxx',
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            'dataType': 'json',

            success: function(response){
                console.log('success')
            },
            error: function(response){
                console.log('error')
            }

        })
    })
})
