define(['jquery', 'bootstrap'], function ($) {
    $(document).ready(function () {
        console.log("chargement JS ajax-course-complement.js OK");


        $('.publication_div').hide();
        $("#id_is_publish").on('change', function (event) {
            $('.publication_div').toggle(500);
        });
 
        $('#id_is_publish').prop('checked', true); 
 
         $('#id_is_share').prop('checked', true); 

 
        $('#id_is_task').prop('checked', false); 
        $('#id_is_paired').prop('checked', false); 
        $('#id_notification').prop('checked', false); 


});

});

