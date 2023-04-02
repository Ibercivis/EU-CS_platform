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




