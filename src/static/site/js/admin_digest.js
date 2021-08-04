jQuery(function ($) {
    $('.test').click(function(e){
        e.preventDefault()
        console.log('test')
        $.ajax({
            type: 'POST',
            url: '/digest/sendTest',
            success: function(response){
                console.log('success')
            },
            error: function(response){
                console.log('error')
            }

        })
    })
})
