const CardManager = {
    clickOnHeart: function(project_id){
        $.ajax({
            type: 'POST',
            url: '/likeProjectAjax',
            data: {project_id: project_id},
            success: function(response){
                console.log(response)
                var hijo = $('#heart'+project_id).find(".value")
                var valor = parseInt(hijo.text(),10);
                if(response['Liked'] === "True"){
                    $('#heart'+project_id).addClass("animate__animated animate__fadeIn text-danger")
                    $('#heart'+project_id).removeClass("text-muted")
                    valor ++;
                    $('#heart'+project_id).one("animationend", function() {
                        $('#heart'+project_id).removeClass("animate__animated animate__fadeIn ");
                    });
                }else{
                    $('#heart'+project_id).addClass("animate__animated animate__fadeIn text-muted")
                    $('#heart'+project_id).removeClass("text-danger")
                    valor--;
                    $('#heart'+project_id).one("animationend", function() {
                        $('#heart'+project_id).removeClass("animate__animated animate__fadeIn");
                    });
                }
                hijo.text(valor);

            },
            error: function(response){
                console.log(response)
            },
        })
    },

    clickOnFollow: function(project_id){
        $.ajax({
            type: 'POST',
            url: '/followProjectAjax',
            data: {project_id: project_id},
            success: function(response){
                console.log(response)
                var hijo = $('#follow'+project_id).find(".value")
                var valor = parseInt(hijo.text(),10);
                if(response['Followed'] === "True"){
                    $('#follow'+project_id).addClass("animate__animated animate__fadeIn text-primary")
                    $('#follow'+project_id).removeClass("text-muted")
                    valor ++;
                    $('#follow'+project_id).one("animationend", function() {
                        $('#follow'+project_id).removeClass("animate__animated animate__fadeIn ");
                    });
                }else{
                    $('#follow'+project_id).addClass("animate__animated animate__fadeIn text-muted")
                    $('#follow'+project_id).removeClass("text-primary")
                    valor--;
                    $('#follow'+project_id).one("animationend", function() {
                        $('#follow'+project_id).removeClass("animate__animated animate__fadeIn");
                    });
                }
                hijo.text(valor);

            },
            error: function(response){
                console.log(response)
            },
        })
    }
};
$(document).ready(function() {
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', getCSRFToken());
        }
    });
    $(".heart").on("click", function() {
        // Código que se ejecutará cuando se haga clic en el elemento con el ID "mi-boton"
        console.log("heart clicked");
        CardManager.clickOnHeart($(this).attr('project_id'))
    });
    $(".followIcon").on("click", function() {
        // Código que se ejecutará cuando se haga clic en el elemento con el ID "mi-boton"
        console.log("follow clicked");
        CardManager.clickOnFollow($(this).attr('project_id'))
    });

    // Enable tooltips everywhere
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })
    
    $('.copyLink').on('click', async function(event) {
        const link = $(this).attr('url');
        console.log('jere');
        try {
          await navigator.clipboard.writeText(link);
        } catch (err) {
          console.error('Error copying link: ', err);
        }
    });

    $('#accordion-filters').on('show.bs.collapse', function(e) {
        $('#accordion-button').css('opacity', '0');
        $('#accordion-button').html('Hide filters <i class="fa-solid fa-chevron-up">').css('opacity', '1');;

    });

    $('#accordion-filters').on('hide.bs.collapse', function(e) {
        $('#accordion-button').css('opacity', '0');
        $('#accordion-button').html('Show filters <i class="fa-solid fa-chevron-down">').css('opacity', '1');;

    });

});
$(function() {
    $('.doModalAction').click(function(){
        console.log($(this).attr('id'))
        var action=$(this).attr('id')
        if(action == 'deletePlatform'){
            var actionFriend='delete this platform'
            var buttonAction='<button type="button" class="btn btn-danger" id="deletePlatformButton">Yes!, delete it</button>'
        }
        $('#myModalTitle').html('Are you sure you want to '+actionFriend+'?')
        $('#myModalBody').html('Caution!, this is permanent and can not be undone')
        $('#myModalFooter').html(
            buttonAction+
            '<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>'
        )
        $('#myModal').modal('toggle')

        if(action == 'deletePlatform'){
            attatchDeletePlatform()
        }
    })
    $(document).on('click', '.redirect', function(){
        console.log('redirect')
        window.location.href=$(this).val()
    })
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })


})

function attatchDeletePlatform(){
    $('#deletePlatformButton').click(function(){
        console.log('Deleted')
        console.log($('#Id').attr('id'))
        $.ajax({
            type: 'GET',
            url: '/deletePlatformAjax/'+$('#Id').val(),
            data: {id: $('Id').attr('id')},
            success: function(response){
                $('#myModalTitle').html('The platform was deleted')
                $('#myModalBody').html('You can close this window')
                $('#myModalFooter').html('<button type="button" class="btn btn-secondary redirect" value="/platforms" data-dismiss="modal" >Close</button>')

            },
            error: function(response){
                $('#myModalBody').html('Ops, something went wrong')
                $('#deletePlatformButton').hide()

            }
        })
    })
}

function createChart(labels, accesses, likes, follows, div_id) {
    const ctx = document.getElementById(div_id).getContext('2d');

    const chart = new Chart(ctx, {
        type: 'bar', // You can change the chart type (e.g., 'bar', 'line', 'pie', etc.)
        data: {
            labels: labels, // The x-axis labels (days)
            datasets: [{
                label: 'Accesses', // The label for the dataset
                data: accesses, // The y-axis values
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            },
            {
                label: 'Likes', // The label for the dataset
                data: likes, // The y-axis values
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            },
            {
                label: 'Follows', // The label for the dataset
                data: follows, // The y-axis values
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    type: 'time',
                    time: {
                        unit: 'week'
                    }
                },
            }
        }
    });
}

function generateProjectStats(project_id, div_id){
    $.ajax({
        type: 'POST',
        url: '/generateProjectStatsAjax',
        dataType: 'json',
        data: {project_id: project_id},
        success: function(response){
            console.log(response)
            console.log(typeof(response))
            var html = '<div class="row">'
            var days = []
            var accesses = []
            var likes = []
            var follows = []
            html += '<div class="col-12 mb-5">'
            html += '<h5>Project '+response[0]['project__name']+'</h5>'
            $.each(response, function(key, value){
                days.push(Date.parse(value['day']))
                accesses.push(value['accesses'])
                likes.push(value['likes'])
                follows.push(value['follows'])
            })
            html += '<canvas id="project_chart'+project_id+'" width="400" height="150"></canvas>'
            html += '</div>'
            $('#project_stats_'+project_id).html(html)
            createChart(days, accesses, likes, follows, 'project_chart'+project_id)
        },

        error: function(response){
            console.log(response)
        }
    })
}    
  
$(document).ready(function() {
    $('.btn-scroll').on('click', function(event) {
      event.preventDefault();
      var sectionId = $(this).attr('href');
      var sectionPosition = $(sectionId).offset().top;
      var offset = -143; // El desplazamiento que quieres aplicar
  
      $('html, body').animate({
        scrollTop: sectionPosition + offset
      }, 400); // Puedes ajustar la duración de la animación según necesites
    });
  });

/* SearchBar */

$(document).ready(function() {
    // Expande la barra de búsqueda cuando se hace clic en cualquier parte de ella
    $('.search-container').click(function() {
        var $container = $(this);
        // Asegúrate de expandir solo si no está ya expandida
        if (!$container.hasClass('expanded')) {
            $container.addClass('expanded');
            // Iniciar la transición de los botones después de que la barra se haya expandido
            setTimeout(function() {
                $container.find('.sub-nav-bar').addClass('show-buttons');
            }, 300); // Asegúrate de que este temporizador coincida con la duración de la transición CSS
        }
    });

    // Expandir la barra de búsqueda al hacer clic en el input si no está expandida
    $('#keywords').on('click', function() {
        var $container = $(this).closest('.search-container');
        if (!$container.hasClass('expanded')) {
            $container.addClass('expanded');
            // Iniciar la transición de los botones después de que la barra se haya expandido
            setTimeout(function() {
                $container.find('.sub-nav-bar').addClass('show-buttons');
            }, 300); // Asegúrate de que este temporizador coincida con la duración de la transición CSS
        }
    });
  
    // Colapsa la barra de búsqueda cuando se hace clic fuera de ella y no hay texto
    $(document).click(function(event) {
      if (!$(event.target).closest('.search-container').length) {
        var $container = $('.search-container');
        // Verifica si hay texto en el input
        if ($('#keywords').val() === '') {
          $('.search-container').removeClass('expanded');
          // Eliminar la clase que muestra los botones inmediatamente
          $container.find('.sub-nav-bar').removeClass('show-buttons');
        }
      }
    });
  
    // Evita que los clics dentro de la barra de búsqueda la colapsen
    $('.search-container input, .search-container .sub-nav-bar').click(function(event) {
      event.stopPropagation(); // Detiene la propagación del evento para no activar el colapso
    });
  });

  // Animation for content numbers
  $(document).ready(function () {
    function animateNumbers() {
        $('.number').each(function () {
            $(this).prop('Counter', 0).animate({
            Counter: $(this).text()
            }, {
            duration: 2000,
            easing: 'swing',
            step: function (now) {
                $(this).text(Math.ceil(now));
            }
            });
        });
    }

    $(window).one('scroll', function () {
        // Mostrar por consola cuántos pixeles se han hecho scroll
        console.log($(this).scrollTop());

        console.log
        if ($(this).scrollTop() > 500) {
            console.log("You've scrolled 500 pixels.");
            animateNumbers();
        }
    });
});






