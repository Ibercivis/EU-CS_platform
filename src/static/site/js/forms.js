$(function() {
    var imgSelected
    var $image = $('#image')
    var canvasData;
    var cropBoxData;

      $(".fileUpload").change(function () {
        imgSelected=$(this).attr('name')
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $("#image").attr("src", e.target.result);
                $("#modalCrop").modal("show");
            }
            reader.readAsDataURL(this.files[0]);
        }
      });
      $(".js-zoom-in").click(function () {
        $image.cropper("zoom", 0.1);
      });

      $(".js-zoom-out").click(function () {
        $image.cropper("zoom", -0.1);
      });

    /* Scripts to handle the cropper box */
    $("#modalCrop").on("shown.bs.modal",function(){
        $image.cropper({
            viewMode:1,
            aspectRatio: imgSelected == 'profileImage' ? 11/4 : 3/2,
            minCropBoxWidth: imgSelected == 'profileImage' ? 1100 : 600,
            minCropBoxHeight: 400,
            dragMode: 'move',
            guides: false,
            center: false,
            highlight: false,
            cropBoxResizable: false,
            toggleDragModeOnDblclick: false,
            ready: function(){
                $image.cropper('setCanvasData', canvasData)
                $image.cropper('setCropBoxData', cropBoxData);
            }
        })
    }).on('hidden.bs.modal', function(){
        cropBoxData = $image.cropper('getCropBoxData')
        canvasData = $image.cropper('getCanvasData');
        $image.cropper('destroy')
    })

    /* Script to collect the data and post to the server  */
    $(".js-crop-and-upload").click(function () {
        var cropData = $image.cropper("getData");
        $("#id_x" + imgSelected).val(cropData["x"]);
        $("#id_y" + imgSelected).val(cropData["y"]);
        $("#id_height" + imgSelected).val(cropData["height"]);
        $("#id_width" + imgSelected).val(cropData["width"]);
        $("#modalCrop").modal("hide");
        $('#imageResult' + imgSelected).attr('src', $image.cropper('getCroppedCanvas',
            {width: imgSelected == 'profileImage' ? 1100 : 600, height: 400}).toDataURL());
    });



    /* Clear error fields when clicking */
    $('input').on('focus', function(){
        if($(this).is('.error'))
            $(this).removeClass('error');
    });
    $('select').on('focus', function(){
        if($(this).is('.error'))
            $(this).removeClass('error');
    });
    $('.select2-selection--multiple').on('focus', function(){
        if($(this).is('.error'))
            $(this).removeClass('error');
    });

    for(var instanceName in CKEDITOR.instances){
        CKEDITOR.instances[instanceName].on('focus', function(e){
            id='#cke_'+$(this).attr('name')
            if($(id).is('.error'))
                $(id).removeClass('error');
        })
    }





    /* form scripts */
    $('.submit').click(function(e){
        e.preventDefault()

        /* To check that we click on Save & continue  */
        if($(this).hasClass('continue'))
            var contin=true
        else
            var contin=false
        $('.myerror').remove()
        $.ajaxSettings.traditional = true;
        for(var instanceName in CKEDITOR.instances)
            CKEDITOR.instances[instanceName].updateElement();

        var form_id = $(this).parents('form:first').attr('id')
        var url = '/save'+form_id+'Ajax/'
        console.log('submit')
        $.ajax({
            type: 'POST',
            url: url,
            processData: false,
            contentType: false,
            data: new FormData(document.getElementById(form_id)),
            success: function(response){
                if(contin){
                    $('#Id').val(response.Id)
                    console.log('continue')
                    $('.savedInfo').html('<span class="alert alert-success fade show">'+
                            '<i class="fas fa-check"></i> Saved</span>').show().fadeOut(2500)

                }else{
                }
            },
            error: function (response){
                if(response.status==500){
                    alert('Unexpected error, please contact with the administrator')
                }
                $.each(response.responseJSON, function(i,val){
                    $('#id_'+i).addClass('error')
                    $('#id_'+i).parent().find('.select2-selection--multiple').addClass('error')
                    $('#hint_id_'+i).append('<div class="myerror small text-danger">'+val+'</div>')
                    $('#cke_id_'+i).addClass('error')
                })
                $('html, body').animate({
                    scrollTop: $('.myerror:visible:first').offset().top-100
                }, 1000);
            }
       })

    })




})
