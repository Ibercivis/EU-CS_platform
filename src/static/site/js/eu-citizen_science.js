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
                $('#myModalFooter').html('<button type="button" class="btn btn-secondary redirect" value="platforms" data-dismiss="modal" >Close</button>')

            },
            error: function(response){
                $('#myModalBody').html('Ops, something went wrong')
                $('#deletePlatformButton').hide()

            }
        })
    })
}
